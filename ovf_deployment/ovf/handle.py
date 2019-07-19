
import os
import uuid
import pathlib
import tarfile
import logging
from pyVmomi import vim, VmomiSupport
from ovf_deployment.log.setup import addClassLogger


logger = logging.getLogger(__name__)


@addClassLogger
class FileHandle(object):
    def __init__(self, filename):
        self.filename = filename
        self.fh = open(filename, 'rb')
        self.path = pathlib.Path(filename)

        self.st_size = os.stat(filename).st_size
        self.offset = 0

    def __del__(self):
        self.fh.close()

    def __str__(self):
        return self.filename

    def tell(self):
        return self.fh.tell()

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset

        return self.fh.seek(offset, whence)

    def seekable(self):
        return True

    def read(self, amount):
        self.offset += amount
        result = self.fh.read(amount)
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)


@addClassLogger
class OvfHandler(object):

    def __init__(self, ovf_file_path, vcenter_handle):
        self.uuid = uuid.uuid4().__str__()
        self.file_path = ovf_file_path
        self.ovf_mgr = OvfManager(vcenter_handle)
        self.file = None
        self.ovf_descriptor = None
        self.json_descriptor = {}
        self.ova_file = None
        self.ovf_file = None
        self.vmdks = []
        self.manifest_file = None
        self.ovf_cert = None
        self.file_list = []
        self.working_dir = None

        if not self._validate_file_path():
            self.__log.exception("File path does not exist: {}".format(self.file_path))
            raise FileExistsError("File path does not exist: {}".format(self.file_path))

        self._collect_files()
        self.read_ovf_descriptor()

    def _validate_file_path(self):
        self.file = pathlib.Path(self.file_path)
        return self.file.exists()

    def _collect_files(self):
        self.__log.info('Collecting the Files for the OVF/OVA: {}'.format(self.ova_file))
        try:
            if self.file.suffix == '.ova':
                self.__log.info('File Type is OVA')
                self.__log.info('Extracting files from OVA ...')
                self.ova_file = FileHandle(self.file)
                tar = tarfile.open(fileobj=self.ova_file)
                self.working_dir = self.file.parent.joinpath(self.uuid)
                self.__log.debug('OVA Working Directory: {}'.format(self.working_dir))
                tar.extractall(path=self.working_dir)
                self.file_list = [FileHandle(filename=self.working_dir.joinpath(f)) for f in tar.getnames()]

            elif self.file.suffix == '.ovf':
                self.__log.info('File Type is OVA')
                self.ova_file = None
                self.working_dir = self.file.parent.joinpath(self.uuid)
                self.__log.debug('OVA Working Directory: {}'.format(self.working_dir))
                self.file_list = [
                    FileHandle(filename=self.file.parent.joinpath(f.name)) for f in self.file.parent.iterdir() if not
                    f.stem.find(self.file.stem) == -1
                ]

            self.__log.info('File List: \n{}'.format(self.file_list))

            for fh in self.file_list:
                if fh.path.suffix == '.cert':
                    self.ovf_cert = fh
                elif fh.path.suffix == '.ovf':
                    self.ovf_file = fh
                elif fh.path.suffix == '.mf':
                    self.manifest_file = fh
                elif fh.path.suffix == '.vmdk':
                    self.vmdks.append(fh)

        except BaseException as e:
            self.__log.exception('Exception: {} \n Args: {}'.format(e, e.args))
            raise e

    def read_ovf_descriptor(self):
        self.__log.info('Reading in the OVF descriptor in XML format')
        self.ovf_descriptor = self.ovf_file.read(self.ovf_file.st_size).decode()

    def _cleanup_extracted_files(self):
        return

    def parse_descriptor(self):
        self.__log.info('Parsing in the OVF descriptor')
        self.ovf_mgr.parse_descriptor(self.ovf_descriptor)

    def get_descriptor_json(self):
        self.__log.info('Converting ovf_descriptor to JSON')
        try:
            dict_descriptor = {
                'annotation': self.ovf_mgr.parsed_descriptor.annotation,
                'defaultDeploymentOption': self.ovf_mgr.parsed_descriptor.defaultDeploymentOption,
                'defaultEntityName': self.ovf_mgr.parsed_descriptor.defaultEntityName,
                'deploymentOption': [
                    {
                        'key': '',
                        'label': '',
                        'description': ''
                    }
                ],
                'eula': list(self.ovf_mgr.parsed_descriptor.eula),
                'ipAllocationScheme': list(self.ovf_mgr.parsed_descriptor.ipAllocationScheme),
                'ipProtocols': list(self.ovf_mgr.parsed_descriptor.ipProtocols),
                'network': [
                    {
                        'name': '',
                        'description': ''
                    }
                ],
                'productInfo': {
                    'appUrl': '',
                    'fullVersion': '',
                    'instanceId': '',
                    'key': 0,
                    'name': '',
                    'vendor': '',
                    'vendorUrl': '',
                    'version': ''
                },
                'property': {
                    'categoryName': [
                        {
                            'id': '',
                            'key': 0,
                            'instanceId': '',
                            'label': '',
                            'type': '',
                            'typeReference': '',
                            'userConfigurable': True or False,
                            'value': ''
                        },
                    ]
                },
                'virtualApp': self.ovf_mgr.parsed_descriptor.virtualApp,
            }
            print('')
        except BaseException as e:
            self.__log.exception('Exception: {} \n Args: {}'.format(e, e.args))
            raise e


@addClassLogger
class OvfManager(object):

    def __init__(self, vcenter_handle):
        self.vcenter = vcenter_handle
        self.manager = self.vcenter.content.ovfManager
        self.pdp = vim.OvfManager.ParseDescriptorParams()
        self.parsed_descriptor = None
        self.vm_folder_tree = []  # Datacenter > parent_folder > sub_folders in dict format
        self.hosts_and_clusters_tree = {}  # Datacenter > cluster > hosts of clusters
        self.portgroups = {}  # Datacenter > VDS > PortGroup
        self.hosts_to_vds_map = {}  # Vmhost: VDS
        self.network_map = []
        self.property_map = []
        self.dest_cluster = None
        self.dest_host = None
        self.dest_datastore = None
        self.dest_resource_pool = None
        self.dest_vm_folder = None
        self.dict_tracker = {}

        self._build_folder_tree(self.vcenter.content.rootFolder)

    def parse_descriptor(self, ovf_descriptor):
        self.__log.info('Parsing in the OVF descriptor')
        self.parsed_descriptor = self.manager.ParseDescriptor(ovf_descriptor, self.pdp)

    def _build_folder_tree(self, rootFolder):
        self.__log.info('Building the vCenter Folder tree')
        try:
            for dc in rootFolder.childEntity:
                dict_handler = {}
                dict_handler.update(self._traverse_vm_tree(dc.vmFolder))
                dict_handler['name'] = dc.name
                dict_handler['_moId'] = dc._moId
                self.vm_folder_tree.append(dict_handler)
        except BaseException as e:
            self.__log.exception('Exception: {} \n Args: {}'.format(e, e.args))
            raise e

    def _traverse_vm_tree(self, entity):
        dict_tracker = {}
        try:
            if isinstance(entity, vim.Folder):
                dict_tracker.update({
                    'name': entity.name,
                    '_moId': entity._moId,
                    'sub_folders': []
                })
                if entity.childEntity:
                    for child in entity.childEntity:
                        if isinstance(child, vim.Folder):
                            dict_tracker['sub_folders'].append(self._traverse_vm_tree(child))
                    return dict_tracker
                return
            else:
                return
        except BaseException as e:
            self.__log.exception('Exception: {} \n Args: {}'.format(e, e.args))
            raise e


@addClassLogger
class vmFolder(object):

    def __init__(self, vmFolder):
        self._moId = vmFolder._moId
        self.name = vmFolder.name
        self.parent_moId = vmFolder.parent._moId
        self.children = []

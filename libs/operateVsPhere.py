# -*- coding: utf-8 -*-
# @Time    : 2021/6/22 14:22
# @Author  : weidengyi

"""
参考：
https://github.com/reubenur-rahman/vmware-pyvmomi-examples/blob/master/create_and_remove_snapshot.py
快照管理，只能还原到一级目录一个快照名，如果有多级，可以用snapshot.childSnapshotList判断，在遍历
参考：https://www.cnpython.com/qa/139558
"""


import ssl
import atexit
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect, GetSi


class OperateVSphere():

    def __init__(self, host, user, password, port):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        # self.si = self.init_connect()

    def init_connect(self):
        try:
            context = None
            if hasattr(ssl, '_create_unverified_context'):
                context = ssl._create_unverified_context()
            self.si = SmartConnect(host=self.host, user=self.user, pwd=self.password, port=self.port, sslContext=context)
            atexit.register(Disconnect, self.si)  # 有异常时退出
            # return si
            return True
        except IOError as e:
            return None

    def get_vm_obj(self, content, vimtype, name):
        """
         Get the vsphere object associated with a given text name
        """
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    # 任务
    def wait_for_tasks(self, tasks):
        pc = self.si.content.propertyCollector
        task_list = [str(task) for task in tasks]
        obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task) for task in tasks]
        prop_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task, pathSet=[], all=True)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        filter_spec.propSet = [prop_spec]
        filters = pc.CreateFilter(filter_spec, True)
        try:
            version, state = None, None
            while len(task_list):
                update = pc.WaitForUpdates(version)
                for filterSet in update.filterSet:
                    for objSet in filterSet.objectSet:
                        task = objSet.obj
                        for change in objSet.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                            elif change.name == 'info.state':
                                state = change.val
                            else:
                                continue
                            if not str(task) in task_list:
                                continue
                            if state == vim.TaskInfo.State.success:
                                task_list.remove(str(task))
                            elif state == vim.TaskInfo.State.error:
                                raise task.info.error
                version = update.version
        finally:
            if filters:
                filters.Destroy()

    def get_vmstatus(self, vm_name):
        """# 获取虚拟机状态"""
        pass

    def create_snapshot(self, vm_name, snapshot_name):
        description = "rpm make snapshot"
        # Read about dumpMemory : http://pubs.vmware.com/vi3/sdk/ReferenceGuide/vim.VirtualMachine.html#createSnapshot
        dump_memory = False
        quiesce = True

        content = self.si.RetrieveContent()
        vm = self.get_vm_obj(content, [vim.VirtualMachine], vm_name)
        task = [vm.CreateSnapshot(snapshot_name, description, dump_memory, quiesce)]
        self.wait_for_tasks(task)

    def del_snapshot(self, vm_name, snapshot_name):
        """删除快照"""
        try:
            content = self.si.RetrieveContent()
            vm = self.get_vm_obj(content, [vim.VirtualMachine], vm_name)
            snapshots = vm.snapshot.rootSnapshotList
            for snapshot in snapshots:
                print("snapshot:", snapshot.name)
                if snapshot.name == snapshot_name:
                    snap_obj = snapshot.snapshot
                    task = [snap_obj.RemoveSnapshot_Task(True)]
                    self.wait_for_tasks(task)
                    return True
            return False
        except:
            return False

    # 恢复快照
    def re_snapshot(self, vm_name, snapshot_name):
        content = self.si.RetrieveContent()
        vm = self.get_vm_obj(content, [vim.VirtualMachine], vm_name)
        # print(vm.summary.runtime.powerState)
        snapshots = vm.snapshot.rootSnapshotList
        for snapshot in snapshots:
            if snapshot.name == snapshot_name:
                snap_obj = snapshot.snapshot
                self.wait_for_tasks([snap_obj.RevertToSnapshot_Task()]  )
                # print(vm.summary.runtime.powerState)
                if vm.summary.runtime.powerState == 'poweredOff':
                    self.wait_for_tasks([vm.PowerOnVM_Task()])
                return True
        return False

    # 获取快照信息
    def get_snapshot_info(self, vm_name, snapshot_name):
        content = self.si.RetrieveContent()
        vm = self.get_vm_obj(content, [vim.VirtualMachine], vm_name)
        snapshots = vm.snapshot.rootSnapshotList
        for snapshot in snapshots:
            if snapshot.name == snapshot_name:
                return snapshot

    def get_vm_info(self, vm_name):
        content = self.si.RetrieveContent()
        vm = self.get_vm_obj(content, [vim.VirtualMachine], vm_name)
        return vm.summary.runtime


if __name__ == "__main__":
    from libs.RemoteOperate import RemoteModule
    import time
    host = '10.1.107.200'
    user = 'zhanglichao'
    password = 'zhanglichao@zdns'
    port = 443
    snapshot_name = "初始环境"
    vm_name = "10.1.107.31-centos64"


    operate_VSphere = OperateVSphere(host, user, password, port)
    print(type(operate_VSphere.init_connect()))
    # remote_exec = RemoteModule(ip='10.1.107.31', port=22, user='root', passwd='zdns@knet.cn')

    # 恢复快照
    time.sleep(10)
    is_re_snapshot_ok = operate_VSphere.re_snapshot(vm_name, snapshot_name)
    print("is_re_snapshot_ok:", is_re_snapshot_ok)

    get_info = operate_VSphere.get_vm_info(vm_name)
    print('get_info:', get_info, get_info.powerState, dir(get_info))
    # 在zddi-build-7.8的目录执行git pull
    # res = remote_exec.exec_cmd("cd /root/zddi-build-v4/ && git pull")
    # print("res:", res)
    # res = remote_exec.exec_cmd("cd /root/zddi-build-v4/ && git checkout -f master")
    # print("res:", res)
    # 删除快照
    # is_del_snapshot_ok = operate_VSphere.del_snapshot(vm_name, snapshot_name)
    # print("is_del_snapshot_ok:", is_del_snapshot_ok)
    # 打快照
    # operate_VSphere.create_snapshot(vm_name, snapshot_name)
#

# context = None
# if hasattr(ssl, '_create_unverified_context'):
#     context = ssl._create_unverified_context()
# si = SmartConnect(host=host, user=user, pwd=password, port=port, sslContext=context)
# if not si:
#     print("帐号密码有问题")
#     atexit.register(Disconnect, si)
#
#
# # 任务
# def WaitForTasks(tasks, si):
#     pc = si.content.propertyCollector
#     task_list = [str(task) for task in tasks]
#     obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task) for task in tasks]
#     prop_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task, pathSet=[], all=True)
#     filter_spec = vmodl.query.PropertyCollector.FilterSpec()
#     filter_spec.objectSet = obj_specs
#     filter_spec.propSet = [prop_spec]
#     filter = pc.CreateFilter(filter_spec, True)
#     try:
#         version, state = None, None
#         while len(task_list):
#             update = pc.WaitForUpdates(version)
#             for filterSet in update.filterSet:
#                 for objSet in filterSet.objectSet:
#                     task = objSet.obj
#                     for change in objSet.changeSet:
#                         if change.name == 'info':
#                             state = change.val.state
#                         elif change.name == 'info.state':
#                             state = change.val
#                         else:
#                             continue
#                         if not str(task) in task_list:
#                             continue
#                         if state == vim.TaskInfo.State.success:
#                             task_list.remove(str(task))
#                         elif state == vim.TaskInfo.State.error:
#                             raise task.info.error
#             version = update.version
#     finally:
#         if filter:
#             filter.Destroy()
#
#
# # 获取虚拟机状态
# def getvmstatus(vm_name):
#     content = si.RetrieveContent()
#     for child in content.rootFolder.childEntity:
#         if hasattr(child, 'vmFolder'):
#             datacenter = child
#             vmFolder = datacenter.vmFolder
#             vmList = vmFolder.childEntity
#             for vm in vmList:
#                 print(dir(vm.name))
#                 # if vm.summary.config.name == vm_name:
#                 #     print(vm.summary.runtime.powerState)
#
# # 查看快照信息
# def get_vmsnapshotinfo(vm_name):
#     content = si.RetrieveContent()
#     container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
#     for c in container.view:
#         if c.name == vm_name:
#             snapshots = c.snapshot.rootSnapshotList
#             return snapshots
#
#
# # 获取虚拟机列表
# def get_vmlist():
#     content = si.RetrieveContent()
#     container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
#     return container.view
#
#
# # 创建快照
# def create_snapshot(vm_name):
#     description = "Test snapshot"
#     snapshot_name = "my_test_snapshot"
#     # Read about dumpMemory : http://pubs.vmware.com/vi3/sdk/ReferenceGuide/vim.VirtualMachine.html#createSnapshot
#     dump_memory = False
#     quiesce = True
#     for vm in get_vmlist():
#         if vm.name == vm_name:
#             task = [vm.CreateSnapshot(snapshot_name, description, dump_memory, quiesce)]
#             WaitForTasks(task, si)
#             return True
#     return False
#
# # 删除快照
# def del_snapshot(vm_name, snapshot_name):
#     for vm in get_vmlist():
#         if vm.name == vm_name:
#             snapshots = vm.snapshot.rootSnapshotList
#             for snapshot in snapshots:
#                 if snapshot.name == snapshot_name:
#                     snap_obj = snapshot.snapshot
#                     task = [snap_obj.RemoveSnapshot_Task()]
#                     WaitForTasks(task, si)
#                     return True
#     return False
#
# # 恢复快照
# def re_snapshot(vm_name, snapshot_name):
#     for vm in get_vmlist():
#         if vm.name == vm_name:
#             snapshots = vm.snapshot.rootSnapshotList
#             for snapshot in snapshots:
#                 if snapshot.name == snapshot_name:
#                     snap_obj = snapshot.snapshot
#                     task = [snap_obj.RevertToSnapshot_Task()]
#                     WaitForTasks(task, si)
#                     break
# print(del_snapshot("10.1.107.31", 'my_test_snapshot'))
# # re_snapshot("10.1.107.31", "初始环境")
#
#
#     # for vm in get_vmlist():
#     #     pass
#     #     #print(vm.name)
#     #     if vm.name == vm_name:
#     #         snapshots = vm.snapshot.rootSnapshotList
#     #         for snapshot in snapshots:
#     #             print(snapshot.name)
#     #             if snapshot_name == snapshot.name:
#     #                 snap_obj = snapshot.snapshot
#     #                 print("恢复快照", snapshot.name)
#     #                 task = [snap_obj.RevertToSnapshot_Task()]
#     #                 WaitForTasks(task, si)
#
# # print(get_vmsnapshotinfo('10.1.107.31'))
#
# # content = si.RetrieveContent()
# # container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
# # vmList = container.view
# # snapshots = vmList[388].snapshot.rootSnapshotList
# # snap_obj = snapshots[0].snapshot
# # task = [snap_obj.RevertToSnapshot_Task()]
# # WaitForTasks(task, si)



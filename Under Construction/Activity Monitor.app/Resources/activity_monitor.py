#!/usr/bin/env python3

import os
import signal
import sys
import time

import psutil
from PyQt5.QtCore import (
    QTimer,
    Qt,
    QSize,
    pyqtSignal as Signal,
    QItemSelectionModel,
    QItemSelection,
    QObject,
    QThread

)
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QTabWidget,
    QWidget,
    QToolBar,
    QVBoxLayout,
    QAbstractItemView,
    QShortcut,
    QLabel,
    QAction,
    QActionGroup,
    QWidgetAction,
    QMenuBar,
    QComboBox,
    QSizePolicy,
    QLineEdit,
    QTreeView,
)

from activity_monitor.libs.about import About
from activity_monitor.libs.utils import bytes2human
from activity_monitor.libs.tab_cpu import TabCpu
from activity_monitor.libs.tab_system_memory import TabSystemMemory
from activity_monitor.libs.tab_disk_usage import TabDiskUsage
from activity_monitor.libs.tab_disk_activity import TabDiskActivity

__app_name__ = "Activity Monitor"
__app_version__ = "0.1a"
__app_authors__ = ["Hierosme Alias Tuuux", "Contributors ..."]
__app_description__ = "View CPU, Memory, Network, Disk activities and interact with processes"
__app_url__ = "https://github.com/helloSystem/Utilities"


class PSUtilsWorker(QObject):
    finished = Signal()
    # CPU
    updated_cpu_user = Signal(float)
    updated_cpu_system = Signal(float)
    updated_cpu_idle = Signal(float)
    updated_cpu_cumulative_threads = Signal(int)
    updated_cpu_process_number = Signal(int)

    # System Memory
    updated_system_memory_total = Signal(str)
    updated_system_memory_available = Signal(str)
    updated_system_memory_percent = Signal(str)
    updated_system_memory_used = Signal(str)
    updated_system_memory_free = Signal(str)
    updated_system_memory_active = Signal(str)
    updated_system_memory_inactive = Signal(str)
    updated_system_memory_buffers = Signal(str)
    updated_system_memory_cached = Signal(str)
    updated_system_memory_shared = Signal(str)
    updated_system_memory_slab = Signal(str)
    updated_system_memory_wired = Signal(str)

    # System Memory Chart Pie
    updated_system_memory_free_raw = Signal(int)
    updated_system_memory_wired_raw = Signal(int)
    updated_system_memory_active_raw = Signal(int)
    updated_system_memory_inactive_raw = Signal(int)

    # Disk Usage
    updated_mounted_disk_partitions = Signal(dict)

    def refresh(self):
        cpu_times_percent = psutil.cpu_times_percent()
        self.updated_cpu_user.emit(cpu_times_percent.user)
        self.updated_cpu_system.emit(cpu_times_percent.system)
        self.updated_cpu_idle.emit(cpu_times_percent.idle)

        # CPU
        cumulative_threads = 0
        process_number = 0
        # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.oneshot
        p = psutil.Process()
        with p.oneshot():
            # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.process_iter
            for proc in psutil.process_iter():
                try:
                    cumulative_threads += proc.num_threads()
                    process_number += 1
                except psutil.NoSuchProcess:
                    pass
        self.updated_cpu_cumulative_threads.emit(cumulative_threads)
        self.updated_cpu_process_number.emit(process_number)

        # System Memory
        virtual_memory = psutil.virtual_memory()
        if hasattr(virtual_memory, "total"):
            self.updated_system_memory_total.emit(bytes2human(virtual_memory.total))
        if hasattr(virtual_memory, "available"):
            self.updated_system_memory_available.emit(bytes2human(virtual_memory.available))
        if hasattr(virtual_memory, "percent"):
            self.updated_system_memory_percent.emit(bytes2human(virtual_memory.percent))
        if hasattr(virtual_memory, "used"):
            self.updated_system_memory_used.emit(bytes2human(virtual_memory.used))
        if hasattr(virtual_memory, "free"):
            self.updated_system_memory_free.emit(bytes2human(virtual_memory.free))
            self.updated_system_memory_free_raw.emit(virtual_memory.free)
        if hasattr(virtual_memory, "active"):
            self.updated_system_memory_active.emit(bytes2human(virtual_memory.active))
            self.updated_system_memory_active_raw.emit(virtual_memory.active)
        if hasattr(virtual_memory, "inactive"):
            self.updated_system_memory_inactive.emit(bytes2human(virtual_memory.inactive))
            self.updated_system_memory_inactive_raw.emit(virtual_memory.inactive)
        if hasattr(virtual_memory, "buffers"):
            self.updated_system_memory_buffers.emit(bytes2human(virtual_memory.buffers))
        if hasattr(virtual_memory, "cached"):
            self.updated_system_memory_cached.emit(bytes2human(virtual_memory.cached))
        if hasattr(virtual_memory, "shared"):
            self.updated_system_memory_shared.emit(bytes2human(virtual_memory.shared))
        if hasattr(virtual_memory, "slab"):
            self.updated_system_memory_slab.emit(bytes2human(virtual_memory.slab))
        if hasattr(virtual_memory, "wired"):
            self.updated_system_memory_wired.emit(bytes2human(virtual_memory.wired))
            self.updated_system_memory_wired_raw.emit(virtual_memory.wired)
        # Disks usage
        data = {}
        item_number = 0
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            data[item_number] = {
                "device": part.device,
                "total": bytes2human(usage.total),

                "used": bytes2human(usage.used),
                "used_in_bytes": f"{'{:,}'.format(usage.used)} bytes",
                "used_raw": usage.used,
                "free": bytes2human(usage.free),
                "free_in_bytes": f"{'{:,}'.format(usage.free)} bytes",
                "free_raw": usage.free,
                "percent": int(usage.percent),
                "fstype": part.fstype,
                "mountpoint": part.mountpoint,

            }
            item_number += 1
        self.updated_mounted_disk_partitions.emit(data)

        self.finished.emit()




class TabNetwork(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setupUI()

    def setupUI(self):
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        layout_grid = QGridLayout()

        # Add spacing on the Tab
        widget_grid = QWidget()
        widget_grid.setLayout(layout_grid)

        space_label = QLabel("")
        layout_vbox = QVBoxLayout()
        layout_vbox.addWidget(space_label)
        layout_vbox.addWidget(widget_grid)
        layout_vbox.setSpacing(0)
        layout_vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout_vbox)

    def refresh(self):
        pass


class ProcessMonitor(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QGridLayout()

        self.searchLineEdit = None
        self.filterComboBox = None
        self.tree_view_model = None
        self.process_tree = None
        self.tree_view_model = None
        self.kill_process_action = None
        self.inspect_process_action = None
        self.selected_pid = -1
        self.my_username = os.getlogin()
        self.header = ["Process ID", "Process Name", "User", "% CPU", "# Threads", "Real Memory", "Virtual Memory"]

        self.setupUi()

    def setupUi(self):
        self.tree_view_model = QStandardItemModel()

        self.process_tree = QTreeView()
        self.process_tree.setModel(self.tree_view_model)
        self.process_tree.setIconSize(QSize(16, 16))
        self.process_tree.setUniformRowHeights(True)
        self.process_tree.setSortingEnabled(True)
        self.process_tree.sortByColumn(3, Qt.DescendingOrder)
        self.process_tree.setAlternatingRowColors(True)
        self.process_tree.clicked.connect(self.onClicked)
        self.process_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.process_tree.setSelectionMode(QAbstractItemView.SingleSelection)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.process_tree)
        self.setLayout(layout)

        self.refresh()

    def save_selection(self):
        selection = self.process_tree.selectionModel().selectedRows()
        blocks = []
        for count, index in enumerate(sorted(selection)):
            row = index.row()

            if count > 0 and row == block[1] + 1:
                block[1] = row
            else:
                block = [row, row]
                blocks.append(block)
        return blocks

    def create_selection(self, blocks):
        mod = self.process_tree.model()
        columns = mod.columnCount() - 1
        flags = QItemSelectionModel.Select
        selection = QItemSelection()
        for start, end in blocks:
            start, end = mod.index(start, 0), mod.index(end, columns)
            if selection.indexes():
                selection.merge(QItemSelection(start, end), flags)
            else:
                selection.select(start, end)
        self.process_tree.selectionModel().clear()
        self.process_tree.selectionModel().select(selection, flags)

    def filter_by_line(self, row, text):
        if hasattr(self.searchLineEdit, "text") and self.searchLineEdit.text():
            if self.searchLineEdit.text() in text:
                return row
            else:
                return None
        else:
            return row

    def refresh(self):
        self.tree_view_model = QStandardItemModel()

        for p in psutil.process_iter():
            with p.oneshot():
                row = [
                    QStandardItem(f"{p.pid}"),
                    QStandardItem(f"{p.name()}"),
                    QStandardItem(f"{p.username()}"),
                    QStandardItem(f"{p.cpu_percent()}"),
                    QStandardItem(f"{p.num_threads()}"),
                    QStandardItem(f"{bytes2human(p.memory_info().rss)}"),
                    QStandardItem(f"{bytes2human(p.memory_info().vms)}"),
                ]

                # Filter Line
                filtered_row = None
                if hasattr(self.searchLineEdit, "text") and self.searchLineEdit.text():
                    if self.searchLineEdit.text() in p.name():
                        filtered_row = row
                else:
                    filtered_row = row

                # Filter by ComboBox index
                #             0: 'All Processes',
                #             1: 'All Processes, Hierarchically',
                #             2: 'My Processes',
                #             3: 'System Processes',
                #             4: 'Other User Processes',
                #             5: 'Active Processes',
                #             6: 'Inactive Processes',
                #             7: 'Windowed Processes',
                #             8: 'Selected Processes',
                #             9: 'Application in last 12 hours',
                if hasattr(self.filterComboBox, "currentIndex"):
                    combo_box_current_index = self.filterComboBox.currentIndex()
                    if combo_box_current_index == 0:
                        pass

                    if combo_box_current_index == 1:
                        pass
                    else:
                        pass

                    if combo_box_current_index == 2:
                        if p.username() == self.my_username:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 3:
                        if p.uids().real < 1000:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 4:
                        if p.username() != self.my_username:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 5:
                        pass
                    elif combo_box_current_index == 6:
                        pass
                    elif combo_box_current_index == 7:
                        pass

                    if combo_box_current_index == 8:
                        if p.pid == self.selected_pid:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                    if combo_box_current_index == 9:
                        if (time.time() - p.create_time()) % 60 <= 43200:
                            filtered_row = self.filter_by_line(filtered_row, p.name())
                        else:
                            filtered_row = None

                if filtered_row:
                    self.tree_view_model.appendRow(filtered_row)

        for pos, title in enumerate(self.header):
            self.tree_view_model.setHeaderData(pos, Qt.Horizontal, title)

        self.process_tree.setModel(self.tree_view_model)

        for pos, title in enumerate(self.header):
            self.process_tree.resizeColumnToContents(pos)

        if self.selected_pid >= 0:
            self.selectItem(str(self.selected_pid))


    def selectClear(self):
        self.selected_pid = -1
        self.process_tree.clearSelection()
        self.kill_process_action.setEnabled(False)
        self.inspect_process_action.setEnabled(False)
        if self.filterComboBox.currentIndex() == 8:
            self.filterComboBox.setCurrentIndex(0)
        self.filterComboBox.model().item(8).setEnabled(False)

    def selectItem(self, itemOrText):
        oldIndex = self.process_tree.selectionModel().currentIndex()
        newIndex = None
        try:  # an item is given--------------------------------------------
            newIndex = self.process_tree.model().indexFromItem(itemOrText)
        except:  # a text is given and we are looking for the first match---
            # for toto in self.process_tree.model().index(0, 0):
            #     print(toto)
            listIndexes = self.process_tree.model().match(
                self.process_tree.model().index(0, 0), Qt.DisplayRole, itemOrText, Qt.MatchStartsWith
            )
            if listIndexes:
                newIndex = listIndexes[0]
        if newIndex:
            self.process_tree.selectionModel().select(  # programmatically selection---------
                newIndex, QItemSelectionModel.ClearAndSelect
            )

    def onClicked(self):
        self.selected_pid = int(self.tree_view_model.itemData(self.process_tree.selectedIndexes()[0])[0])
        if self.selected_pid:
            self.kill_process_action.setEnabled(True)
            self.inspect_process_action.setEnabled(True)
            self.filterComboBox.model().item(8).setEnabled(True)

    def killProcess(self):
        if self.selected_pid:
            os.kill(self.selected_pid, signal.SIGKILL)

    def killSelectedProcess(self):
        if self.selected_pid and self.selected_pid != -1:
            try:
                os.kill(self.selected_pid, signal.SIGKILL)
                self.selected_pid = -1
                self.process_tree.clearSelection()
                self.process_tree.refresh()
            except (Exception, BaseException):
                pass

    def InspectSelectedProcess(self):
        selected = self.process_tree.currentItem()
        if selected is not None:
            pid = int(selected.text(0))
            try:
                self.selected_pid = -1
            except (Exception, BaseException):
                pass


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.hide()

        self.icon_size = 32
        self.filters = [
            "All Processes",
            "All Processes, Hierarchically",
            "My Processes",
            "System Processes",
            "Other User Processes",
            "Active Processes",
            "Inactive Processes",
            "Windowed Processes",
            "Selected Processes",
            "Application in last 12 hours",
        ]

        # vars
        self.threads = []
        self.filterComboBox = None
        self.searchLineEdit = None
        self.process_monitor = None

        self.tab_cpu = None
        self.tab_system_memory = None
        self.tab_disk_activity = None
        self.tab_disk_usage = None
        self.tab_network = None
        self.timer = None

        self.setupUi()

        self.timer.timeout.connect(self.refresh)
        self.refresh()

    def setupUi(self):
        self.setWindowTitle("Activity Monitor")
        self.resize(800, 600)
        self.setWindowIcon(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "Processes.png",
                )
            )
        )
        self.timer = QTimer()
        self._timer_change_for_5_secs()
        self.tab_cpu = TabCpu()
        self.tab_system_memory = TabSystemMemory()
        self.tab_disk_usage = TabDiskUsage()
        self.tab_disk_activity = TabDiskActivity()
        self.tab_network = TabNetwork()
        self.searchLineEdit = QLineEdit()
        # self.searchLineEdit.setStyleSheet("QLineEdit {  border: 2px inner gray;"
        #                                 "border-radius: 30px}")
        self.filterComboBox = QComboBox()

        self.process_monitor = ProcessMonitor()
        self.process_monitor.filterComboBox = self.filterComboBox
        self.process_monitor.searchLineEdit = self.searchLineEdit

        # Ping / Pong for ComboBox
        self.searchLineEdit.textChanged.connect(self.process_monitor.refresh)
        self.filterComboBox.currentIndexChanged.connect(self._filter_by_changed)

        self._createMenuBar()
        self._createActions()
        self._createToolBars()

        self.process_monitor.kill_process_action = self.kill_process_action
        self.process_monitor.inspect_process_action = self.inspect_process_action

        quitShortcut1 = QShortcut(QKeySequence("Escape"), self)
        quitShortcut1.activated.connect(self.process_monitor.selectClear)

        self.setStyleSheet(
            """
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabWidget::pane { /* The tab widget frame */
                position: absolute;
                top: -0.9em;
            }
            """
        )

        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        tabs.addTab(self.tab_cpu, "CPU")
        tabs.addTab(self.tab_system_memory, "System Memory")
        tabs.addTab(self.tab_disk_activity, "Disk Activity")
        tabs.addTab(self.tab_disk_usage, "Disk Usage")
        tabs.addTab(self.tab_network, "Network")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.process_monitor, 1)
        layout.addWidget(QLabel(""))
        layout.addWidget(tabs)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def createThread(self):
        thread = QThread()
        worker = PSUtilsWorker()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.refresh())

        # CPU
        worker.updated_cpu_user.connect(self.tab_cpu.refresh_user)
        worker.updated_cpu_system.connect(self.tab_cpu.refresh_system)
        worker.updated_cpu_idle.connect(self.tab_cpu.refresh_idle)
        worker.updated_cpu_cumulative_threads.connect(self.tab_cpu.refresh_cumulative_threads)
        worker.updated_cpu_process_number.connect(self.tab_cpu.refresh_process_number)

        # System MEmory
        # worker.updated_system_memory_total.connect(self.tab_system_memory.refresh_total)
        worker.updated_system_memory_available.connect(self.tab_system_memory.refresh_available)
        worker.updated_system_memory_used.connect(self.tab_system_memory.refresh_used)
        worker.updated_system_memory_free.connect(self.tab_system_memory.refresh_free)
        worker.updated_system_memory_active.connect(self.tab_system_memory.refresh_active)
        worker.updated_system_memory_inactive.connect(self.tab_system_memory.refresh_inactive)
        worker.updated_system_memory_buffers.connect(self.tab_system_memory.refresh_buffers)
        worker.updated_system_memory_cached.connect(self.tab_system_memory.refresh_cached)
        worker.updated_system_memory_shared.connect(self.tab_system_memory.refresh_shared)
        worker.updated_system_memory_slab.connect(self.tab_system_memory.refresh_slab)
        worker.updated_system_memory_wired.connect(self.tab_system_memory.refresh_wired)

        # System Memory Chart Pie
        worker.updated_system_memory_free_raw.connect(self.tab_system_memory.refresh_free_raw)
        worker.updated_system_memory_wired_raw.connect(self.tab_system_memory.refresh_wired_raw)
        worker.updated_system_memory_active_raw.connect(self.tab_system_memory.refresh_active_raw)
        worker.updated_system_memory_inactive_raw.connect(self.tab_system_memory.refresh_inactive_raw)

        # Disk Usage
        worker.updated_mounted_disk_partitions.connect(self.tab_disk_usage.setMoutedDiskPartitions)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        return thread

    def refresh(self):
        self.process_monitor.refresh()

        self.threads.clear()
        self.threads = [self.createThread()]
        for thread in self.threads:
            thread.start()

    def _close(self):
        self.close()
        return 0

    def _window_minimize(self):
        self.showMinimized()

    def _timer_change_for_1_sec(self):
        self.timer.start(1000)

    def _timer_change_for_3_secs(self):
        self.timer.start(3000)

    def _timer_change_for_5_secs(self):
        self.timer.start(5000)

    def _filter_by_changed(self):
        #             0: 'All Processes',
        #             1: 'All Processes, Hierarchically',
        #             2: 'My Processes',
        #             3: 'System Processes',
        #             4: 'Other User Processes',
        #             5: 'Active Processes',
        #             6: 'Inactive Processes',
        #             7: 'Windowed Processes',
        #             8: 'Selected Processes',
        #             9: 'Application in last 12 hours',
        if hasattr(self.filterComboBox, "currentIndex"):
            if self.filterComboBox.currentIndex() == 0:
                self.ActionMenuViewAllProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 1:
                self.ActionMenuViewAllProcessesHierarchically.setChecked(True)
            elif self.filterComboBox.currentIndex() == 2:
                self.ActionMenuViewMyProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 3:
                self.ActionMenuViewSystemProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 4:
                self.ActionMenuViewOtherUserProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 5:
                self.ActionMenuViewActiveProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 6:
                self.ActionMenuViewInactiveProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 7:
                self.ActionMenuViewWindowedProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 8:
                self.ActionMenuViewSelectedProcesses.setChecked(True)
            elif self.filterComboBox.currentIndex() == 9:
                self.ActionMenuViewApplicationInLast12Hours.setChecked(True)

        self.process_monitor.refresh()

    def _filter_by_all_processes(self):
        self.filterComboBox.setCurrentIndex(0)

    def _filter_by_all_process_hierarchically(self):
        self.filterComboBox.setCurrentIndex(1)

    def _filter_by_my_processes(self):
        self.filterComboBox.setCurrentIndex(2)

    def _filter_by_system_processes(self):
        self.filterComboBox.setCurrentIndex(3)

    def _filter_by_other_user_processes(self):
        self.filterComboBox.setCurrentIndex(4)

    def _filter_by_active_processes(self):
        self.filterComboBox.setCurrentIndex(5)

    def _filter_by_inactive_processes(self):
        self.filterComboBox.setCurrentIndex(6)

    def _filter_by_windowed_processes(self):
        self.filterComboBox.setCurrentIndex(7)

    def _filter_by_selected_processes(self):
        self.filterComboBox.setCurrentIndex(8)

    def _filter_by_application_in_last_12_hours(self):
        self.filterComboBox.setCurrentIndex(9)

    def _createMenuBar(self):
        self.menuBar = QMenuBar()

        # File Menu
        fileMenu = self.menuBar.addMenu("&File")

        quitAct = QAction("Quit", self)
        quitAct.setStatusTip("Quit this application")
        quitAct.setShortcut(QKeySequence.Quit)
        quitAct.triggered.connect(self._close)

        fileMenu.addAction(quitAct)

        # Edit Menu
        editMenu = self.menuBar.addMenu("&Edit")

        # View Menu
        viewMenu = self.menuBar.addMenu("&View")

        view_columns = viewMenu.addMenu("Columns")
        view_columns.setEnabled(False)

        view_dock = viewMenu.addMenu("Dock Icon")
        view_dock.setEnabled(False)

        # Update Frequency Menu
        viewMenuUpdateFrequency = viewMenu.addMenu("Update Frequency")

        ActionMenuViewUpdateFrequency5Secs = QAction("5 Secs", self)
        ActionMenuViewUpdateFrequency5Secs.setCheckable(True)
        ActionMenuViewUpdateFrequency5Secs.triggered.connect(self._timer_change_for_5_secs)

        ActionMenuViewUpdateFrequency3Secs = QAction("3 Secs", self)
        ActionMenuViewUpdateFrequency3Secs.setCheckable(True)
        ActionMenuViewUpdateFrequency3Secs.triggered.connect(self._timer_change_for_3_secs)

        ActionMenuViewUpdateFrequency1Sec = QAction("1 Secs", self)
        ActionMenuViewUpdateFrequency1Sec.setCheckable(True)
        ActionMenuViewUpdateFrequency1Sec.triggered.connect(self._timer_change_for_1_sec)

        update_frequency_group = QActionGroup(self)
        update_frequency_group.addAction(ActionMenuViewUpdateFrequency1Sec)
        update_frequency_group.addAction(ActionMenuViewUpdateFrequency3Secs)
        update_frequency_group.addAction(ActionMenuViewUpdateFrequency5Secs)

        ActionMenuViewUpdateFrequency5Secs.setChecked(True)

        viewMenuUpdateFrequency.addAction(ActionMenuViewUpdateFrequency1Sec)
        viewMenuUpdateFrequency.addAction(ActionMenuViewUpdateFrequency3Secs)
        viewMenuUpdateFrequency.addAction(ActionMenuViewUpdateFrequency5Secs)

        viewMenu.addSeparator()

        self.ActionMenuViewAllProcesses = QAction("All Processes", self)
        self.ActionMenuViewAllProcesses.setCheckable(True)
        self.ActionMenuViewAllProcesses.triggered.connect(self._filter_by_all_processes)

        self.ActionMenuViewAllProcessesHierarchically = QAction("All Processes, Hierarchically", self)
        self.ActionMenuViewAllProcessesHierarchically.setCheckable(True)
        self.ActionMenuViewAllProcessesHierarchically.triggered.connect(self._filter_by_all_process_hierarchically)

        self.ActionMenuViewMyProcesses = QAction("My Processes", self)
        self.ActionMenuViewMyProcesses.setCheckable(True)
        self.ActionMenuViewMyProcesses.triggered.connect(self._filter_by_my_processes)

        self.ActionMenuViewSystemProcesses = QAction("System Processes", self)
        self.ActionMenuViewSystemProcesses.setCheckable(True)
        self.ActionMenuViewSystemProcesses.triggered.connect(self._filter_by_system_processes)

        self.ActionMenuViewOtherUserProcesses = QAction("Other User Processes", self)
        self.ActionMenuViewOtherUserProcesses.setCheckable(True)
        self.ActionMenuViewOtherUserProcesses.triggered.connect(self._filter_by_other_user_processes)

        self.ActionMenuViewActiveProcesses = QAction("Active Processes", self)
        self.ActionMenuViewActiveProcesses.setCheckable(True)
        self.ActionMenuViewActiveProcesses.triggered.connect(self._filter_by_active_processes)

        self.ActionMenuViewInactiveProcesses = QAction("Inactive Processes", self)
        self.ActionMenuViewInactiveProcesses.setCheckable(True)
        self.ActionMenuViewInactiveProcesses.triggered.connect(self._filter_by_inactive_processes)

        self.ActionMenuViewWindowedProcesses = QAction("Windowed Processes", self)
        self.ActionMenuViewWindowedProcesses.setCheckable(True)
        self.ActionMenuViewWindowedProcesses.triggered.connect(self._filter_by_windowed_processes)

        self.ActionMenuViewSelectedProcesses = QAction("Selected Processes", self)
        self.ActionMenuViewSelectedProcesses.setCheckable(True)
        self.ActionMenuViewSelectedProcesses.setEnabled(False)
        self.ActionMenuViewSelectedProcesses.triggered.connect(self._filter_by_selected_processes)

        self.ActionMenuViewApplicationInLast12Hours = QAction("Application in last 12 hours", self)
        self.ActionMenuViewApplicationInLast12Hours.setCheckable(True)
        self.ActionMenuViewApplicationInLast12Hours.triggered.connect(self._filter_by_application_in_last_12_hours)

        alignmentViewBy = QActionGroup(self)
        alignmentViewBy.addAction(self.ActionMenuViewAllProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewAllProcessesHierarchically)
        alignmentViewBy.addAction(self.ActionMenuViewMyProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewSystemProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewOtherUserProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewActiveProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewInactiveProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewWindowedProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewSelectedProcesses)
        alignmentViewBy.addAction(self.ActionMenuViewApplicationInLast12Hours)

        self.ActionMenuViewAllProcesses.setChecked(True)

        viewMenu.addActions(
            [
                self.ActionMenuViewAllProcesses,
                self.ActionMenuViewAllProcessesHierarchically,
                self.ActionMenuViewMyProcesses,
                self.ActionMenuViewSystemProcesses,
                self.ActionMenuViewOtherUserProcesses,
                self.ActionMenuViewActiveProcesses,
                self.ActionMenuViewInactiveProcesses,
                self.ActionMenuViewWindowedProcesses,
                self.ActionMenuViewSelectedProcesses,
                self.ActionMenuViewApplicationInLast12Hours,
            ]
        )

        viewMenu.addSeparator()

        viewFilterProcesses = QAction("Filter Processes", self)
        viewFilterProcesses.setShortcut("Ctrl+Meta+F")
        viewFilterProcesses.setEnabled(False)

        viewInspectProcess = QAction("Inspect Process", self)
        viewInspectProcess.setShortcut("Ctrl+I")
        viewInspectProcess.setEnabled(False)

        viewSampleProcess = QAction("Sample Process", self)
        viewSampleProcess.setShortcut("Ctrl+Meta+S")
        viewSampleProcess.setEnabled(False)

        viewRunSpindump = QAction("Run Spindump", self)
        viewRunSpindump.setShortcut("Alt+Ctrl+Meta+S")
        viewRunSpindump.setEnabled(False)

        viewRunSystemDiagnostics = QAction("Run system Diagnostics", self)
        viewRunSystemDiagnostics.setEnabled(False)

        viewQuitProcess = QAction("Quit Process", self)
        viewQuitProcess.setShortcut("Ctrl+Meta+Q")
        viewQuitProcess.setEnabled(False)

        viewSendSignalToProcesses = QAction("Send Signal to Processes", self)
        viewSendSignalToProcesses.setEnabled(False)

        viewShowDeltasForProcess = QAction("Show Deltas for Process", self)
        viewShowDeltasForProcess.setShortcut("Ctrl+Meta+J")
        viewShowDeltasForProcess.setEnabled(False)

        viewMenu.addActions(
            [
                viewFilterProcesses,
                viewInspectProcess,
                viewSampleProcess,
                viewRunSpindump,
                viewRunSystemDiagnostics,
                viewQuitProcess,
                viewSendSignalToProcesses,
                viewShowDeltasForProcess,
            ]
        )

        viewMenu.addSeparator()

        viewClearCPUHistory = QAction("Clear CPU History", self)
        viewClearCPUHistory.setShortcut("Ctrl+K")
        viewClearCPUHistory.setEnabled(False)

        viewEnterFullScreen = QAction("Enter Full Screen", self)
        viewEnterFullScreen.setEnabled(False)

        viewMenu.addActions(
            [
                viewClearCPUHistory,
                viewEnterFullScreen,
            ]
        )

        # Window Menu
        windowMenu = self.menuBar.addMenu("Window")

        ActionMenuWindowMinimize = QAction("Minimize", self)
        ActionMenuWindowMinimize.setShortcut("Ctrl+M")
        ActionMenuWindowMinimize.triggered.connect(self._window_minimize)

        self.ActionMenuWindowZoom = QAction("Zoom", self)
        self.ActionMenuWindowZoom.setEnabled(False)

        windowMenu.addAction(ActionMenuWindowMinimize)
        windowMenu.addAction(self.ActionMenuWindowZoom)
        windowMenu.addSeparator()

        ActionMenuWindowActivityMonitor = QAction("Activity Monitor", self)
        ActionMenuWindowActivityMonitor.setShortcut("Ctrl+1")
        ActionMenuWindowActivityMonitor.setEnabled(False)

        windowMenu.addAction(ActionMenuWindowActivityMonitor)

        # Help Menu
        helpMenu = self.menuBar.addMenu("&Help")

        aboutAct = QAction("&About", self)
        aboutAct.setStatusTip("About this application")
        aboutAct.triggered.connect(self._showAbout)

        helpMenu.addAction(aboutAct)

        self.setMenuBar(self.menuBar)

    def _createActions(self):
        self.kill_process_action = QAction(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "KillProcess.png",
                )
            ),
            "Quit Process",
            self,
        )
        self.kill_process_action.setStatusTip("Kill process")
        self.kill_process_action.triggered.connect(self.process_monitor.killSelectedProcess)
        self.kill_process_action.setEnabled(False)

        self.inspect_process_action = QAction(
            QIcon(
                os.path.join(
                    os.path.dirname(__file__),
                    "activity_monitor",
                    "ui",
                    "Inspect.png",
                )
            ),
            "Inspect",
            self,
        )
        self.inspect_process_action.setStatusTip("Inspect the selected process")
        self.inspect_process_action.setEnabled(False)
        # self.inspect_process_action.triggered.connect(self.InspectSelectedProcess)

        showLabel = QLabel("Show")
        showLabel.setAlignment(Qt.AlignCenter)

        showVBoxLayout = QVBoxLayout()

        self.filterComboBox.addItems(self.filters)
        self.filterComboBox.model().item(8).setEnabled(False)

        self.filterComboBox.setCurrentIndex(0)

        showVBoxLayout.addWidget(self.filterComboBox)
        showVBoxLayout.addWidget(showLabel)

        showWidget = QWidget()
        showWidget.setLayout(showVBoxLayout)

        self.filter_process_action = QWidgetAction(self)
        self.filter_process_action.setDefaultWidget(showWidget)

        searchLabel = QLabel("Search")
        searchLabel.setAlignment(Qt.AlignCenter)

        searchVBoxLayout = QVBoxLayout()
        searchVBoxLayout.addWidget(self.searchLineEdit)
        searchVBoxLayout.addWidget(searchLabel)

        searchWidget = QWidget()
        searchWidget.setLayout(searchVBoxLayout)

        self.search_process_action = QWidgetAction(self)
        self.search_process_action.setDefaultWidget(searchWidget)

    def _createToolBars(self):
        toolbar = QToolBar("Main ToolBar")
        toolbar.setIconSize(QSize(self.icon_size, self.icon_size))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        toolbar.setOrientation(Qt.Horizontal)

        toolbar.addAction(self.kill_process_action)
        toolbar.addAction(self.inspect_process_action)
        toolbar.addAction(self.filter_process_action)
        toolbar.addAction(self.search_process_action)

        self.addToolBar(toolbar)

    @staticmethod
    def _showAbout():
        about = About()
        about.size = 300, 340
        about.icon = QPixmap(
            os.path.join(
                os.path.dirname(__file__),
                "activity_monitor",
                "ui",
                "Processes.png",
            )
        ).scaledToWidth(96, Qt.SmoothTransformation)
        about.name = __app_name__
        about.version = f"Version {__app_version__}"
        about.text = (
            f"This project is open source, contributions are welcomed.<br><br>"
            f"Visit <a href='{__app_url__}'>{__app_url__}</a> for more information, "
            f"report bug or to suggest a new feature<br>"
        )
        about.credit = "Copyright 2023-2023 helloSystem team. All rights reserved"
        about.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        win = Window()
        win.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass

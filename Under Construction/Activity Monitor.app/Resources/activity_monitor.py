#!/usr/bin/env python3

import hashlib
import os
import signal
import sys

import psutil
from PyQt5.QtCore import QTimer, Qt, QSize, pyqtSignal as Signal, QPoint, QObject, QThread
from PyQt5.QtGui import QKeySequence, QIcon, QColor, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QTabWidget,
    QWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QToolBar,
    QVBoxLayout,
    QPushButton,
    QAbstractItemView,
    QShortcut,
    QLabel,
    QColorDialog,
    QAction,
    QWidgetAction,
    QMenuBar,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,

)

from activity_monitor.libs.about import About

__app_name__ = "Activity Monitor"
__app_version__ = "0.1a"
__app_authors__ = ["Hierosme Alias Tuuux", "Contributors ..."]
__app_description__ = "View CPU, Memory, Network, Disk activities and interact with processes"
__app_url__ = "https://github.com/helloSystem/Utilities"


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.80 KB'
    # >>> bytes2human(100001221)
    # '95.40 MB'
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            return f"{round(float(n) / prefix[s], 2):.2f} {s}B"
    return f"{n} B"


class ColorButton(QPushButton):
    """
    Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to the default color (None by default).
    """

    colorChanged = Signal(object)

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color
        self.pressed.connect(self.onColorPicker)

        # Set the initial/default state.
        self.setColor(self._default)
        self.setContentsMargins(3, 3, 3, 3)

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.drawing = False
        self.brushSize = 28
        self.brushColor = Qt.black
        self.lastPoint = QPoint()

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(10, 10)
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color)

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        """
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.
        """
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(self._default)

        return super(ColorButton, self).mousePressEvent(e)


class TabCpu(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # User label
        self.lbl_user = QLabel("User:")
        self.lbl_user.setAlignment(Qt.AlignRight)
        # User label value
        self.lbl_user_value = QLabel("")
        self.lbl_user_value.setAlignment(Qt.AlignRight)
        # User Color button
        self.color_button_user = ColorButton(color="green")
        # Insert user labels on the right position
        self.layout.addWidget(self.lbl_user, 1, 0, 1, 1)
        self.layout.addWidget(self.lbl_user_value, 1, 1, 1, 1)
        self.layout.addWidget(self.color_button_user, 1, 2, 1, 1)

        # System label
        self.lbl_system = QLabel("System:")
        self.lbl_system.setAlignment(Qt.AlignRight)
        # System label value
        self.lbl_system_value = QLabel("")
        self.lbl_system_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_system = ColorButton(color="red")
        # Insert system labels on the right position
        self.layout.addWidget(self.lbl_system, 2, 0, 1, 1)
        self.layout.addWidget(self.lbl_system_value, 2, 1, 1, 1)
        self.layout.addWidget(self.color_button_system, 2, 2, 1, 1)

        # Label Idle
        self.lbl_idle = QLabel("Idle:")
        self.lbl_idle.setAlignment(Qt.AlignRight)
        # Label Idle value
        self.lbl_idle_value = QLabel("")
        self.lbl_idle_value.setAlignment(Qt.AlignRight)
        # User system button
        self.color_button_idle = ColorButton(color="black")

        # Insert idle labels on the right position
        self.layout.addWidget(self.lbl_idle, 3, 0, 1, 1)
        self.layout.addWidget(self.lbl_idle_value, 3, 1, 1, 1)
        self.layout.addWidget(self.color_button_idle, 3, 2, 1, 1)

        # Label threads
        self.lbl_threads = QLabel("Threads:")
        self.lbl_threads.setAlignment(Qt.AlignRight)
        # Label threads value
        self.lbl_threads_value = QLabel("")
        self.lbl_threads_value.setAlignment(Qt.AlignLeft)
        # Insert threads labels on the right position
        self.layout.addWidget(self.lbl_threads, 1, 3, 1, 1)
        self.layout.addWidget(self.lbl_threads_value, 1, 4, 1, 1)

        # Label Processes
        self.lbl_processes = QLabel("Processes:")
        self.lbl_processes.setAlignment(Qt.AlignRight)
        # Label Processes value
        self.lbl_processes_value = QLabel("")
        self.lbl_processes_value.setAlignment(Qt.AlignLeft)
        # Insert Processes labels on the right position
        self.layout.addWidget(self.lbl_processes, 2, 3, 1, 1)
        self.layout.addWidget(self.lbl_processes_value, 2, 4, 1, 1)

        self.lbl_cpu_usage = QLabel("CPU Usage")
        self.lbl_cpu_usage.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_cpu_usage, 0, 6, 1, 1)

        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def refresh(self):
        cpu_times_percent = psutil.cpu_times_percent()
        self.lbl_user_value.setText(f'<font color="{self.color_button_user.color()}">{cpu_times_percent.user} %</font>')
        self.lbl_system_value.setText(
            f'<font color="{self.color_button_system.color()}">{cpu_times_percent.system} %</font>'
        )
        self.lbl_idle_value.setText(f'<font color="{self.color_button_idle.color()}">{cpu_times_percent.idle} %</font>')

        cumulative_threads = 0
        process_number = 0
        # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.oneshot
        p = psutil.Process()
        with p.oneshot():
            # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.process_iter
            for proc in psutil.process_iter():
                try:
                    # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.cpu_times
                    cumulative_threads += proc.num_threads()
                    process_number += 1
                except psutil.NoSuchProcess:
                    pass

        self.lbl_processes_value.setText(f"{process_number}")
        self.lbl_threads_value.setText(f"{cumulative_threads}")


class TabSystemMemoryWorker(QObject):
    finished = Signal()

    def run(self):
        self.finished.emit()


class TabSystemMemory(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # Internal class settings
        __virtual_memory = psutil.virtual_memory()
        self.memory_os_capability = {
            "total": hasattr(__virtual_memory, "total"),
            "available": hasattr(__virtual_memory, "available"),
            "percent": hasattr(__virtual_memory, "percent"),
            "used": hasattr(__virtual_memory, "used"),
            "free": hasattr(__virtual_memory, "free"),
            "active": hasattr(__virtual_memory, "active"),
            "inactive": hasattr(__virtual_memory, "inactive"),
            "buffers": hasattr(__virtual_memory, "buffers"),
            "cached": hasattr(__virtual_memory, "cached"),
            "shared": hasattr(__virtual_memory, "shared"),
            "slab": hasattr(__virtual_memory, "slab"),
            "wired": hasattr(__virtual_memory, "wired"),
        }

        self.layout = QGridLayout()
        # self.layout.setAlignment(Qt.AlignTop)

        self.setLayout(self.layout)

        # widget Position management
        grid_col = 0
        grid_row = 0
        if self.memory_os_capability["free"]:
            # Free label
            self.lbl_free = QLabel("Free:")
            self.lbl_free.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_free_value = QLabel("")
            self.lbl_free_value.setAlignment(Qt.AlignRight)
            self.lbl_free_value.setAlignment(Qt.AlignRight)
            self.lbl_free_value.setToolTip(
                "Memory not being used at all (zeroed) that is readily available; note that this doesn’t reflect the actual memory available (use available instead). total - used does not necessarily match free."
            )
            # Free Color button
            self.color_button_free = ColorButton(color="green")
            # Insert Free labels on the right position
            self.layout.addWidget(self.lbl_free, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_free_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_free, grid_row, grid_col + 2, 1, 1)

            self.layout.setRowStretch(grid_col, 0)
            grid_row += 1

        if self.memory_os_capability["wired"]:
            # Wired label
            self.lbl_wired = QLabel("Wired:")
            self.lbl_wired.setAlignment(Qt.AlignRight)
            # Free label value
            self.lbl_wired_value = QLabel("")
            self.lbl_wired_value.setAlignment(Qt.AlignRight)
            self.lbl_wired_value.setToolTip("Memory that is marked to always stay in RAM. It is never moved to disk.")
            # Free Color button
            self.color_button_wired = ColorButton(color="red")
            # Insert Free labels on the right position
            self.layout.addWidget(self.lbl_wired, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_wired_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_wired, grid_row, grid_col + 2, 1, 1)

            grid_row += 1

        # PSUtil can return active
        if self.memory_os_capability["active"]:
            # Active label
            self.lbl_active = QLabel("Active:")
            self.lbl_active.setAlignment(Qt.AlignRight)
            # Active label value
            self.lbl_active_value = QLabel("")
            self.lbl_active_value.setAlignment(Qt.AlignRight)
            self.lbl_active_value.setToolTip("Memory currently in use or very recently used, and so it is in RAM.")
            # Active Color button
            self.color_button_active = ColorButton(color="orange")
            # Insert Active labels on the right position
            self.layout.addWidget(self.lbl_active, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_active_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_active, grid_row, grid_col + 2, 1, 1)
            grid_row += 1

        # PSUtil can return inactive
        if self.memory_os_capability["inactive"]:
            # Inactive label
            self.lbl_inactive = QLabel("Inactive:")
            self.lbl_inactive.setAlignment(Qt.AlignRight)
            # Inactive label value
            self.lbl_inactive_value = QLabel("")
            self.lbl_inactive_value.setAlignment(Qt.AlignRight)
            self.lbl_inactive_value.setToolTip("Memory that is marked as not used.")
            # Inactive Color button
            self.color_button_inactive = ColorButton(color="blue")
            # Insert Inactive labels on the right position
            self.layout.addWidget(self.lbl_inactive, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_inactive_value, grid_row, grid_col + 1, 1, 1)
            self.layout.addWidget(self.color_button_inactive, grid_row, grid_col + 2, 1, 1)
            grid_row += 1

        # PSUtil can return used
        if self.memory_os_capability["used"]:
            # Used label
            self.lbl_used = QLabel("Used:")
            self.lbl_used.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_used_value = QLabel("")
            self.lbl_used_value.setAlignment(Qt.AlignRight)
            self.lbl_used_value.setToolTip(
                "Memory used, calculated differently depending on the platform and designed for informational purposes only. <b>total - free</b> does not necessarily match <b>used</b>."
            )
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_used, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_used_value, grid_row, grid_col + 1, 1, 1)

        # Position management
        # Set col and row to the second widget Position
        grid_row = 0
        grid_col += 3

        # PSUtil can return available
        if self.memory_os_capability["available"]:
            # Used label
            self.lbl_available = QLabel("Available:")
            self.lbl_available.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_available_value = QLabel("")
            self.lbl_available_value.setAlignment(Qt.AlignRight)
            self.lbl_available_value.setToolTip(
                "The memory that can be given instantly to processes without the system going into swap. <br>"
            )
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_available, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_available_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return buffers
        if self.memory_os_capability["buffers"]:
            # Used label
            self.lbl_buffers = QLabel("Buffers:")
            self.lbl_buffers.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_buffers_value = QLabel("")
            self.lbl_buffers_value.setAlignment(Qt.AlignRight)
            self.lbl_buffers_value.setToolTip("Cache for things like file system metadata.<br>")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_buffers, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_buffers_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return cached
        if self.memory_os_capability["cached"]:
            # Used label
            self.lbl_cached = QLabel("Cached:")
            self.lbl_cached.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_cached_value = QLabel("")
            self.lbl_cached_value.setAlignment(Qt.AlignRight)
            self.lbl_cached_value.setToolTip("Cache for various things.")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_cached, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_cached_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return shared
        if self.memory_os_capability["shared"]:
            # Used label
            self.lbl_shared = QLabel("Shared:")
            self.lbl_shared.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_shared_value = QLabel("")
            self.lbl_shared_value.setAlignment(Qt.AlignRight)
            self.lbl_shared_value.setToolTip("Memory that may be simultaneously accessed by multiple processes.")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_shared, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_shared_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        # PSUtil can return lab
        if self.memory_os_capability["slab"]:
            # Used label
            self.lbl_slab = QLabel("Slab:")
            self.lbl_slab.setAlignment(Qt.AlignRight)
            # Used label value
            self.lbl_slab_value = QLabel("")
            self.lbl_slab_value.setAlignment(Qt.AlignRight)
            self.lbl_slab_value.setToolTip("in-kernel data structures cache.")
            # Insert Used labels on the right position
            self.layout.addWidget(self.lbl_slab, grid_row, grid_col, 1, 1)
            self.layout.addWidget(self.lbl_slab_value, grid_row, grid_col + 1, 1, 1)
            grid_row += 1

        grid_col += 2
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.refresh()

    def refresh(self):
        # >>> psutil.virtual_memory()
        # svmem(total=10367352832, available=6472179712, percent=37.6, used=8186245120,
        # free=2181107712, active=4748992512, inactive=2758115328, buffers=790724608,
        # cached=3500347392, shared=787554304)
        vm = psutil.virtual_memory()
        # Free
        if self.memory_os_capability["free"]:
            self.lbl_free_value.setText(f"<font color={self.color_button_free.color()}>{bytes2human(vm.free)}</font>")

        # Wired
        if self.memory_os_capability["wired"]:
            self.lbl_wired_value.setText(
                f"<font color={self.color_button_wired.color()}>{bytes2human(vm.wired)}</font>"
            )

        # Active
        if self.memory_os_capability["active"]:
            self.lbl_active_value.setText(
                f"<font color={self.color_button_active.color()}>{bytes2human(vm.active)}</font>"
            )

        # Inactive
        if self.memory_os_capability["inactive"]:
            self.lbl_inactive_value.setText(
                f"<font color={self.color_button_inactive.color()}>{bytes2human(vm.inactive)}</font>"
            )

        # Used
        if self.memory_os_capability["used"]:
            self.lbl_used_value.setText(bytes2human(vm.used))

        # Available
        if self.memory_os_capability["available"]:
            self.lbl_available_value.setText(bytes2human(vm.available))

        # Buffers
        if self.memory_os_capability["buffers"]:
            self.lbl_buffers_value.setText(bytes2human(vm.buffers))

        # Cached
        if self.memory_os_capability["cached"]:
            self.lbl_cached_value.setText(bytes2human(vm.cached))

        # Shared
        if self.memory_os_capability["shared"]:
            self.lbl_shared_value.setText(bytes2human(vm.shared))

        # Slab
        if self.memory_os_capability["slab"]:
            self.lbl_slab_value.setText(bytes2human(vm.slab))

        # # VM Size
        # vm_size = 0
        # # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.oneshot
        # p = psutil.Process()
        # with p.oneshot():
        #     # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.process_iter
        #     for proc in psutil.process_iter():
        #         # https://psutil.readthedocs.io/en/latest/index.html?highlight=wired#psutil.Process.memory_info
        #         vm_size += proc.memory_info().vms
        #
        # self.lbl_vm_size_value.setText(bytes2human(vm_size))

        # Swap used
        # self.lbl_swap_used_value.setText(bytes2human(psutil.swap_memory().used))


class TabDiskActivity(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def refresh(self):
        pass


class TabDiskUsage(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def refresh(self):
        pass


class TabNetwork(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def refresh(self):
        pass


class ProcessMonitor(QWidget):
    def __init__(self, parent):
        super(ProcessMonitor, self).__init__(parent)
        self.icon_size = 32
        self.selected_processes_id = [-1]
        self.selected_filter_index = 1
        self.filters = {
            1: 'All Processes',
            2: 'All Processes, Hierarchically',
            3: 'My Processes',
            4: 'System Processes',
            5: 'Other User Processes',
            6: 'Active Processes',
            7: 'Inactive Processes',
            8: 'Windowed Processes',
            9: 'Selected Processes',
            10: 'Application in last 12 hours',
        }

        self.setupUi(parent)

    def setupUi(self, parent):
        self._createActions(parent)
        self._createMenuBar(parent)
        self._createToolBars(parent)

        self.mainLayout = None

        self.quitShortcut1 = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quitShortcut1.activated.connect(self.close)

        self.quitShortcut2 = QShortcut(QKeySequence("Ctrl+W"), self)
        self.quitShortcut2.activated.connect(self.close)

        self.process_tree = QTreeWidget()
        # Set uniform row heights to avoid the treeview from jumping around when refreshing
        self.process_tree.setIconSize(QSize(16, 16))
        self.process_tree.setStyleSheet("QTreeWidget::item { height: 20px; }")

        self.process_tree.setUniformRowHeights(True)
        self.process_tree.setColumnCount(7)
        self.process_tree.setHeaderLabels(
            ["Process ID", "Process Name", "User", "% CPU", "# Threads", "Real Memory", "Virtual Memory"])
        self.process_tree.setSortingEnabled(True)
        self.process_tree.sortByColumn(3, Qt.DescendingOrder)
        self.process_tree.setAlternatingRowColors(True)
        # self.process_tree.itemClicked.connect(self.onClicked)
        # self.process_tree.itemDoubleClicked.connect(self.killProcess)
        self.process_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.process_tree.selectionModel().selectionChanged.connect(self.getItems)

        self.processTree = QTreeWidget()

        # Set uniform row heights to avoid the treeview from jumping around when refreshing
        # self.processTree.setIconSize(QSize(16, 16))
        # self.processTree.setStyleSheet("QTreeWidget::item { height: 20px; }")
        #
        # self.processTree.setUniformRowHeights(True)
        # self.processTree.setColumnCount(4)
        # self.processTree.setHeaderLabels(["Process Name", "Process ID", "Memory", "CPU"])
        # self.processTree.setSortingEnabled(True)
        # self.processTree.sortByColumn(3, Qt.DescendingOrder)
        # self.processTree.setAlternatingRowColors(True)
        # self.processTree.itemClicked.connect(self.onClicked)
        # self.processTree.itemDoubleClicked.connect(self.killProcess)
        self.processTree.setSelectionMode(QAbstractItemView.SingleSelection)

        # Create a QThread object
        self.system_memory_thread = QThread()
        self.system_memory_widget = TabSystemMemory()
        # Create a worker object
        self.system_memory_worker = TabSystemMemoryWorker(self.system_memory_widget)
        # Move worker to the thread
        self.system_memory_worker.moveToThread(self.system_memory_thread)
        # Step 5: Connect signals and slots
        self.system_memory_thread.started.connect(self.system_memory_worker.run)
        self.system_memory_worker.finished.connect(self.system_memory_thread.quit)
        self.system_memory_worker.finished.connect(self.system_memory_worker.deleteLater)
        self.system_memory_thread.finished.connect(self.system_memory_thread.deleteLater)
        # Start the thread
        self.system_memory_thread.start()

        self.tabs = QTabWidget()
        self.tabs.addTab(TabCpu(), "CPU")
        self.tabs.addTab(TabSystemMemory(), "System Memory")
        self.tabs.addTab(TabDiskActivity(), "Disk Activity")
        self.tabs.addTab(TabDiskUsage(), "Disk Usage")
        self.tabs.addTab(TabNetwork(), "Network")

        self.selectedPid = -1

        layout = QVBoxLayout()
        layout.addWidget(self.process_tree)
        # layout.addWidget(self.processTree)
        layout.addWidget(self.tabs)

        self.setLayout(layout)
        self.setStyleSheet(
            """
        QTabWidget::tab-bar {
            alignment: center;
        }"""
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)
        self.refresh()

    def _createActions(self, parent):
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
        self.kill_process_action.setShortcut("Ctrl+k")
        self.kill_process_action.triggered.connect(self.killSelectedProcess)

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
        self.inspect_process_action.setShortcut("Ctrl+i")
        self.inspect_process_action.triggered.connect(self.InspectSelectedProcess)

        self.filterComboBox = QComboBox()
        pos = 0
        self.filterComboBox.addItem('All Processes')
        self.filterComboBox.addItem('All Processes, Hierarchically')
        self.filterComboBox.addItem('My Processes')
        self.filterComboBox.addItem('System Processes')
        self.filterComboBox.addItem('Other User Processes')
        self.filterComboBox.addItem('Active Processes')
        self.filterComboBox.addItem('Inactive Processes')
        self.filterComboBox.addItem('Windowed Processes')
        self.filterComboBox.addItem('Selected Processes')
        self.filterComboBox.addItem('Application in last 12 hours')

        label = QLabel("Show")
        label.setAlignment(Qt.AlignCenter)

        hbox = QVBoxLayout()
        hbox.addWidget(self.filterComboBox)
        hbox.addWidget(label)

        widget = QWidget()
        widget.setLayout(hbox)

        self.filter_process_action = QWidgetAction(self)
        self.filter_process_action.setDefaultWidget(widget)

    def _createToolBars(self, parent):
        toolbar = QToolBar("Main ToolBar")
        toolbar.setIconSize(QSize(self.icon_size, self.icon_size))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setMovable(False)
        toolbar.setOrientation(Qt.Horizontal)

        toolbar.addAction(self.kill_process_action)
        toolbar.addAction(self.inspect_process_action)
        toolbar.addAction(self.filter_process_action)

        parent.addToolBar(toolbar)

    def _createMenuBar(self, parent):
        menuBar = QMenuBar()

        fileMenu = menuBar.addMenu("&File")
        editMenu = menuBar.addMenu("&Edit")

        aboutAct = QAction('&About', parent)
        aboutAct.setStatusTip('About this application')
        aboutAct.triggered.connect(self._showAbout)
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(aboutAct)

        parent.setMenuBar(menuBar)

    def _showAbout(self):
        about = About()
        about.size = 300, 340
        about.icon = QPixmap(
            os.path.join(
                os.path.dirname(__file__),
                "activity_monitor",
                "ui",
                "Processes.png",
            )).scaledToWidth(96, Qt.SmoothTransformation)
        about.name = __app_name__
        about.version = f"Version {__app_version__}"
        about.text = f"This project is open source, contributions are welcomed.<br><br>" \
                     f"Visit <a href='{__app_url__}'>{__app_url__}</a> for more information, " \
                     f"report bug or to suggest a new feature<br>"
        about.credit = "Copyright 2023-2023 helloSystem team. All rights reserved"
        about.show()

    def close(self):
        print("Quitting...")
        sys.exit(0)

    def refresh(self):
        self.refresh_process_tree()
        # self.refreshProcessList()
        # Update active tab only
        self.tabs.currentWidget().refresh()

    def refresh_process_tree(self):

        self.process_tree.clear()
        for p in psutil.process_iter():
            with p.oneshot():
                # print(p.info["pid"])
                # print(p.info["name"])
                item = QTreeWidgetItem()
                item.setText(0, f'{p.pid}')
                item.setText(1, f'{p.name()}')
                item.setText(2, f'{p.username()}')
                item.setText(3, f'{p.cpu_percent()}')
                item.setText(4, f'{p.num_threads()}')
                item.setText(5, f'{bytes2human(p.memory_info().rss)}')
                item.setText(6, f'{bytes2human(p.memory_info().vms)}')
                self.process_tree.addTopLevelItem(item)
                # if p.pid in self.selected_processes_id:
                #     self.process_tree.setCurrentItem(item)
        # item.selectedIndexes(self.selected_processes_id)

        for i in range(self.process_tree.columnCount()):
            self.process_tree.resizeColumnToContents(i)

    def refreshProcessList(self):

        # Calculate total CPU and memory usage
        total_cpu = 0
        total_memory = 0

        self.processTree.clear()
        if os.name == "posix":
            command = "ps -axeo pid,comm,rss,%cpu"
            output = os.popen(command)

            for line in output.readlines():
                data = line.split()
                if data[1] == "COMMAND":
                    continue
                if int(data[0]) < 100:
                    continue
                if len(data) == 4:
                    item = QTreeWidgetItem()
                    item.setText(0, data[1])  # Process Name
                    pid = data[0]

                    if int(pid) == int(self.selectedPid):
                        self.processTree.setCurrentItem(item)
                    item.setText(1, pid)  # PID
                    item.setData(1, 0, data[0])  # Set PID as item.data

                    item.setIcon(0, QIcon.fromTheme("application-x-executable"))

                    # Get the environment variables for the given PID using FreeBSD "procstat penv" command
                    env = {}
                    # env_command = 'procstat penv %s' % pid
                    # env_output = os.popen(env_command)
                    # for env_line in env_output.readlines():
                    #     # Discard everything up to and including ": "
                    #     env_line = env_line[env_line.find(": ") + 2:]
                    #     env_data = env_line.split("=")
                    #     if len(env_data) == 2:
                    #         env[env_data[0]] = env_data[1].strip()

                    # Check whether there is a LAUNCHED_BUNDLE environment variable
                    if "LAUNCHED_BUNDLE" in env:
                        # Without the path, only the bundle name, without the last suffix
                        bundle_path = env["LAUNCHED_BUNDLE"]
                        bundle_name = bundle_path.split("/")[-1].split(".")[0]
                        item.setText(0, bundle_name)

                        # Get the application bundle icon
                        # AppDir
                        if os.path.exists(bundle_path + "/DirIcon"):
                            icon = QIcon(bundle_path + "/DirIcon")
                            item.setIcon(0, icon)
                        else:
                            # .app
                            icon_suffixes = ["png", "jpg", "xpg", "svg", "xpm"]
                            for icon_suffix in icon_suffixes:
                                if os.path.exists(bundle_path + "/Resources/" + bundle_name + "." + icon_suffix):
                                    icon = QIcon(bundle_path + "/Resources/" + bundle_name + "." + icon_suffix)
                                    item.setIcon(0, icon)
                                    break
                        # XDG thumbnails for AppImages; TODO: Test this
                        if bundle_path.endswith(".AppImage"):
                            # xdg_thumbnail_path = os.path.join(xdg.BaseDirectory.xdg_cache_home, "thumbnails", "normal")
                            xdg_thumbnail_path = os.path.expanduser("~/.cache/thumbnails/normal")
                            print(xdg_thumbnail_path)
                            xdg_thumbnail_path = os.path.join(
                                xdg_thumbnail_path, hashlib.md5(bundle_path.encode("utf-8")).hexdigest() + ".png"
                            )
                            if os.path.exists(xdg_thumbnail_path):
                                icon = QIcon(xdg_thumbnail_path)
                                item.setIcon(0, icon)

                    mem = float(data[2])
                    formattedMem = f"{mem / 1024:.0f} MB"  # MB
                    item.setText(2, formattedMem)  # Memory %
                    cpu = float(data[3].replace(",", "."))
                    formattedCpu = f"{cpu:.1f}%"
                    item.setText(3, formattedCpu)  # CPU %
                    self.processTree.addTopLevelItem(item)

                    # Update total CPU and memory usage
                    total_cpu += cpu
                    total_memory += mem

        for i in range(self.processTree.columnCount()):
            self.processTree.resizeColumnToContents(i)

    def getItems(self):
        selected = self.process_tree.selectionModel().selectedIndexes()
        for index in selected:
            print(index)

    def onClicked(self, item):
        print(item.getIndexes())

        # if item and hasattr(item, "text"):
        #     if item.text(0) in self.selected_processes_id:
        #         del self.selected_processes_id[item.text(0)]
        #     else:
        #         self.selected_processes_id.append(item.text(0))

        #
        # print(item)
        # print(item.text(0))
        # pid = int(item.text(0))  # The text in the 2nd column
        # self.selectedPid = item.data(0, 0)

    def killProcess(self, item):
        pid = int(item.text(0))  # The text in the 2nd column
        os.kill(pid, signal.SIGKILL)

    def killSelectedProcess(self):
        selected = self.process_tree.currentItem()
        print(selected)
        if selected is not None:
            pid = int(selected.text(0))
            try:
                os.kill(pid, signal.SIGKILL)
                self.selectedPid = -1
            except:
                pass

    def InspectSelectedProcess(self):
        selected = self.process_tree.currentItem()
        print(selected)
        if selected is not None:
            pid = int(selected.text(0))
            try:
                self.selectedPid = -1
            except:
                pass


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.setupUi()

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
        self.centralWidget = ProcessMonitor(self)
        self.setCentralWidget(self.centralWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        win = Window()
        win.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        pass

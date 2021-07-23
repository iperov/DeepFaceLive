# from PyQt6.QtCore import *
# from PyQt6.QtGui import *
# from PyQt6.QtWidgets import *

# #from localization import StringsDB
# from .QXMainWindow import *

# class QXIconButton(QPushButton):
#     """
#     Custom Icon button that works through keyEvent system, without shortcut of QAction
#     works only with QXMainWindow as global window class
#     currently works only with one-key shortcut
#     """

#     def __init__(self, icon, 
#                     tooltip=None, 
#                     shortcut=None,                    
#                     click_func=None,                  
#                     first_repeat_delay=300,
#                     repeat_delay=20,
#                     ):

#         super().__init__(icon, "")

#         self.setIcon(icon)
        
#         if shortcut is not None:
#             tooltip = f"{tooltip} ( S_HOT_KEY: {shortcut} )"
        
#         self.setToolTip(tooltip)
            
        
        
#         self.seq = QKeySequence(shortcut) if shortcut is not None else None
        
#         QXMainWindow.inst.add_keyPressEvent_listener ( self.on_keyPressEvent )
#         QXMainWindow.inst.add_keyReleaseEvent_listener ( self.on_keyReleaseEvent )
        
#         self.click_func = click_func
#         self.first_repeat_delay = first_repeat_delay
#         self.repeat_delay = repeat_delay
#         self.repeat_timer = None
        
#         self.op_device = None
        
#         self.pressed.connect( lambda : self.action(is_pressed=True)  )
#         self.released.connect( lambda : self.action(is_pressed=False)  )
        
#     def action(self, is_pressed=None, op_device=None):
#         if self.click_func is None:
#             return

#         if is_pressed is not None:
#             if is_pressed:
#                 if self.repeat_timer is None:
#                     self.click_func()
#                     self.repeat_timer = QTimer()
#                     self.repeat_timer.timeout.connect(self.action)
#                     self.repeat_timer.start(self.first_repeat_delay)
#             else:
#                 if self.repeat_timer is not None:
#                     self.repeat_timer.stop()
#                     self.repeat_timer = None
#         else:
#             self.click_func()
#             if self.repeat_timer is not None:
#                 self.repeat_timer.setInterval(self.repeat_delay)
        
#     def on_keyPressEvent(self, ev):              
#         key = ev.nativeVirtualKey()
#         if ev.isAutoRepeat():
#             return
            
#         if self.seq is not None:
#             if key == self.seq[0]:
#                 self.action(is_pressed=True)

#     def on_keyReleaseEvent(self, ev):
#         key = ev.nativeVirtualKey()
#         if ev.isAutoRepeat():
#             return
#         if self.seq is not None:
#             if key == self.seq[0]:
#                 self.action(is_pressed=False)
                
                
############################
############################
############################
############################
############################         
                
# class QXTabWidget(QTabWidget):
#     def __init__(self, tabs=None, tab_shape=None, size_policy=None, maximum_width=None, hided=False, enabled=True):
#         super().__init__()
#         if tabs is not None:
#             for tab,icon,name in tabs:
#                 self.addTab(tab, icon, name)
#         if tab_shape is not None:
#             self.setTabShape(tab_shape)
        
#         if maximum_width is not None:
#             self.setMaximumWidth(maximum_width)
            
#         if size_policy is not None:
#             self.setSizePolicy(*size_policy)
#         if hided:
#             self.hide()
#         self.setEnabled(enabled)
        
        


# class QXComboObjectBox(QXComboBox):
#     """
#     as QComboBox but str'able Iterable of objects 
#     and more functionality    
#     """

#     def __init__(self, choices : Iterable, none_choice=None, font=None, size_policy=None, maximum_width=None, hided=False, enabled=True, on_choosed=None):
#         super().__init__(font=font, size_policy=size_policy, maximum_width=maximum_width, hided=hided, enabled=enabled)
        
#         self.choices = tuple(choices)
#         if len(self.choices) == 0:
#             raise ValueError('Number of choices are 0')
#         self.none_choice = none_choice
#         self.on_choosed = on_choosed

#         if none_choice is not None:
#             self.addItem( QIcon(), str(none_choice) )
#         for i, choice in enumerate(choices):
#             self.addItem( QIcon(), str(choice) )

#         self.setCurrentIndex(0)
#         self.currentIndexChanged.connect(self.on_toggled)
    
#     def get_choices(self):
#         return self.choices
        
#     def get_selected_choice(self):
#         idx = self.currentIndex()
#         if self.none_choice is not None:
#             idx -= 1
#             if idx == -1:
#                 return None

#         return self.choices[idx]

#     def unselect(self, block_signals : bool = False):
#         if self.none_choice is not None:
#             with BlockSignals(self, block_signals=block_signals):
#                 self.setCurrentIndex(0)


#     def set_selected_index(self, index, block_signals : bool = False):
#         if index >= 0 and index < len(self.choices):
#             if self.none_choice is not None:
#                 index += 1

#             with BlockSignals(self, block_signals=block_signals):
#                 self.setCurrentIndex(index)

#     def set_selected_choice(self, choice, block_signals : bool = False):
#         with BlockSignals(self, block_signals=block_signals):
#             if choice is None:
#                 if self.none_choice is not None:
#                     self.setCurrentIndex(0)
#                 else:
#                     raise ValueError('unable to change to None with none_choice=False')
#             else:
#                 for i, schoice in enumerate(self.choices):
#                     if schoice == choice:
#                         self.setCurrentIndex(i+1)
#                         break

#     def on_toggled(self, idx):
#         if self.on_choosed is not None:
#             self.on_choosed( self.get_selected_choice() )
            


# class QXCollapsibleSection(QWidget):
#     def __init__(self, title, content_layout, is_opened=False, allow_open_close=True, show_content_frame=True):
#         super().__init__()

#         btn = self.btn = QToolButton()
#         btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
#         btn.setStyleSheet('border: none;')
#         btn.setArrowType(Qt.ArrowType.RightArrow)
#         btn.setText(title)
#         #btn.setIconSize( QSize(8,8))
#         btn.setCheckable(True)
#         btn.setChecked(False)
        
#         if allow_open_close:
#             btn.toggled.connect(self.on_btn_toggled)

#         line = QXFrame( size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum) )
#         line.setFrameShape(QFrame.Shape.HLine)

#         frame = self.frame = QXFrame( size_policy=(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed), layout=content_layout, hided=True)
#         if show_content_frame:
#             frame.setFrameShape(QFrame.Shape.StyledPanel)

#         main_l = QXGridLayout( contents_margins=0 )

#         main_l.addWidget(btn, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
#         main_l.addWidget(QXHorizontalLine() , 0, 1)

#         main_l.addWidget(frame, 1, 0, 1, 2)
        

#         self.setLayout(main_l)

#         if is_opened:
#             self.open()
#         else:
#             self.close()

#     def is_opened(self):
#         return self.frame.isVisible()
        
#     def open(self):
#         self.btn.setArrowType(Qt.ArrowType.DownArrow)
#         self.frame.show()

#     def close(self):
#         self.btn.setArrowType(Qt.ArrowType.RightArrow)
#         self.frame.hide()

#     def on_btn_toggled(self):
#         if self.btn.isChecked():
#             self.open()
#         else:
#             self.close()

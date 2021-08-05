# -*- coding: utf-8 -*-

# Speed Focus Mode Add-on for Anki
#
# Copyright (C) 2017-2019  Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Modifications to deck options menu.
"""

from anki.hooks import wrap
from aqt.qt import *

from aqt.deckconf import DeckConf
from aqt.forms import dconf

########################################################################

action_spin_items = (
    ("Rate Again", "again"),
    ("Rate Good", "good"),
    ("Bury Card", "bury")
)


def setupUI(self, Dialog):
    self.maxTaken.setMinimum(3)

    grid = QGridLayout()
    label1 = QLabel(self.tab_5)
    label1.setText("Automatically play alert after")
    label2 = QLabel(self.tab_5)
    label2.setText("seconds")
    self.autoAlert = QSpinBox(self.tab_5)
    self.autoAlert.setMinimum(0)
    self.autoAlert.setMaximum(3600)
    grid.addWidget(label1, 0, 0, 1, 1)
    grid.addWidget(self.autoAlert, 0, 1, 1, 1)
    grid.addWidget(label2, 0, 2, 1, 1)
    self.verticalLayout_6.insertLayout(1, grid)

    grid = QGridLayout()
    label1 = QLabel(self.tab_5)
    label1.setText("Automatically show answer after")
    label2 = QLabel(self.tab_5)
    label2.setText("seconds")
    self.autoAnswer = QSpinBox(self.tab_5)
    self.autoAnswer.setMinimum(0)
    self.autoAnswer.setMaximum(3600)
    grid.addWidget(label1, 0, 0, 1, 1)
    grid.addWidget(self.autoAnswer, 0, 1, 1, 1)
    grid.addWidget(label2, 0, 2, 1, 1)
    self.verticalLayout_6.insertLayout(2, grid)

    grid = QGridLayout()
    label1 = QLabel(self.tab_5)
    label1.setText("Automatically")
    label2 = QLabel(self.tab_5)
    label2.setText("after")
    label3 = QLabel(self.tab_5)
    label3.setText("seconds")
    self.autoAction = QComboBox(self.tab_5)
    for label, action in action_spin_items:
        self.autoAction.addItem(label, action)
    self.autoActionTimer = QSpinBox(self.tab_5)
    self.autoActionTimer.setMinimum(0)
    self.autoActionTimer.setMaximum(3600)
    self.autoActionSkipAnswer = QCheckBox(self.tab_5)
    self.autoActionSkipAnswer.setText("Skip answer")
    self.autoActionSkipAnswer.setToolTip("Start counting on question side")
    grid.addWidget(label1, 0, 0, 1, 1)
    grid.addWidget(self.autoAction, 0, 1, 1, 1)
    grid.addWidget(label2, 0, 2, 1, 1)
    grid.addWidget(self.autoActionTimer, 0, 3, 1, 2)
    grid.addWidget(label3, 0, 5, 1, 1)
    grid.addWidget(self.autoActionSkipAnswer, 0, 6, 1, 1)
    spacer = QSpacerItem(40, 10, QSizePolicy.Expanding)
    grid.addItem(spacer, 0, 7, 1, 1)
    self.verticalLayout_6.insertLayout(3, grid)


def load_conf(self):
    f = self.form
    c = self.conf
    f.autoAlert.setValue(c.get('autoAlert', 0))
    f.autoAnswer.setValue(c.get('autoAnswer', 0))
    # keep "autoAgain" as name for legacy reasons
    f.autoActionTimer.setValue(c.get('autoAgain', 0))
    cur_action = c.get('autoAction', "again")
    for index, item in enumerate(action_spin_items):
        if item[1] == cur_action:
            f.autoAction.setCurrentIndex(index)
    f.autoActionSkipAnswer.setChecked(c.get('autoSkip', False))


def save_conf(self):
    f = self.form
    c = self.conf
    c['autoAlert'] = f.autoAlert.value()
    c['autoAnswer'] = f.autoAnswer.value()
    c['autoAgain'] = f.autoActionTimer.value()
    # currentData is not supported on Qt4
    idx = f.autoAction.currentIndex()
    c['autoAction'] = action_spin_items[idx][1]
    c['autoSkip'] = f.autoActionSkipAnswer.isChecked()


def initialize_options():
    dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setupUI)
    DeckConf.loadConf = wrap(DeckConf.loadConf, load_conf)
    DeckConf.saveConf = wrap(DeckConf.saveConf, save_conf, 'before')

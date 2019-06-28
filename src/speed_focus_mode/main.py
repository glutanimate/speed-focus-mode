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
Initializes add-on components.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os

from aqt.qt import *
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.deckconf import DeckConf
from aqt.forms import dconf
from aqt.utils import tooltip

from anki.hooks import addHook, wrap
from anki.sound import play

from .consts import PATH_ADDON, PATH_USERFILES, JSPY_BRIDGE

# Support for custom alert sounds located in user_files dir

alert_name = "alert.mp3"
default_alert = os.path.join(PATH_ADDON, "sounds", alert_name)
user_alert = os.path.join(PATH_USERFILES, alert_name)

if os.path.exists(user_alert):
    ALERT_PATH = user_alert
else:
    ALERT_PATH = default_alert

# OPTIONS
###############################################################################

action_spin_items = (
    ("Rate Again", "again"),
    ("Rate Good", "good"),
    ("Bury Card", "bury")
)

def setup_ui(self, Dialog):
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
    c['autoAction'] = f.autoAction.currentData()
    c['autoSkip'] = f.autoActionSkipAnswer.isChecked()


dconf.Ui_Dialog.setupUi = wrap(dconf.Ui_Dialog.setupUi, setup_ui)
DeckConf.loadConf = wrap(DeckConf.loadConf, load_conf)
DeckConf.saveConf = wrap(DeckConf.saveConf, save_conf, 'before')

# REVIEWER - html and timeouts
###############################################################################

def append_html(self, _old):
    return _old(self) + """
        <script>
            var autoAlertTimeout = 0;
            var autoAnswerTimeout = 0;
            var autoActionTimeout = 0;

            var setAutoAlert = function(ms) {
                clearTimeout(autoAlertTimeout);
                autoAlertTimeout = setTimeout(function () { %s("spdf:alert"); }, ms);
            }
            var setAutoAnswer = function(ms) {
                clearTimeout(autoAnswerTimeout);
                autoAnswerTimeout = setTimeout(function () { %s('ans') }, ms);
            }
            var setAutoAction = function(ms) {
                clearTimeout(autoActionTimeout);
                autoActionTimeout = setTimeout(function () { %s("spdf:action"); }, ms);
            }
        </script>
        """ % (JSPY_BRIDGE, JSPY_BRIDGE, JSPY_BRIDGE)


# set timeouts for auto-alert and auto-reveal
def set_answer_timeouts(self):
    c = mw.col.decks.confForDid(self.card.odid or self.card.did)
    if c.get('autoAnswer', 0) > 0:
        self.bottom.web.eval("setAutoAnswer(%d);" % (c['autoAnswer'] * 1000))
    if c.get('autoAlert', 0) > 0:
        self.bottom.web.eval("setAutoAlert(%d);" % (c['autoAlert'] * 1000))
    if c.get("autoSkip") and c.get('autoAgain', 0) > 0:
        self.bottom.web.eval("setAutoAction(%d);" % (c['autoAgain'] * 1000))

# set timeout for auto-action
def set_question_timeouts(self):
    c = mw.col.decks.confForDid(self.card.odid or self.card.did)
    if not c.get("autoSkip") and c.get('autoAgain', 0) > 0:
        # keep "autoAgain" as name for legacy reasons
        self.bottom.web.eval("setAutoAction(%d);" % (c['autoAgain'] * 1000))


# clear timeouts for auto-alert and auto-reveal, run on answer reveal
def clear_answer_timeouts():
    reviewer = mw.reviewer
    c = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)
    reviewer.bottom.web.eval("""
        if (typeof autoAnswerTimeout !== 'undefined') {
            clearTimeout(autoAnswerTimeout);
        }
        if (typeof autoAlertTimeout !== 'undefined') {
            clearTimeout(autoAlertTimeout);
        }
    """)
    if c.get("autoSkip"):
        reviewer.bottom.web.eval("""
            if (typeof autoActionTimeout !== 'undefined') {
                clearTimeout(autoActionTimeout);
            }
        """)

# clear timeout for auto-action, run on next card
def clear_question_timeouts():
    reviewer = mw.reviewer
    c = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)
    if not c.get("autoSkip"):
        mw.reviewer.bottom.web.eval("""
            if (typeof autoActionTimeout !== 'undefined') {
                clearTimeout(autoActionTimeout);
            }
        """)


Reviewer._bottomHTML = wrap(Reviewer._bottomHTML, append_html, 'around')
Reviewer._showAnswerButton = wrap(
    Reviewer._showAnswerButton, set_answer_timeouts)
Reviewer._showEaseButtons = wrap(Reviewer._showEaseButtons,
                                 set_question_timeouts)
addHook("showAnswer", clear_answer_timeouts)
addHook("showQuestion", clear_question_timeouts)


# REVIEWER - action handler
###############################################################################


def linkHandler(self, url, _old):
    if not url.startswith("spdf"):
        return _old(self, url)
    if not mw.col:
        # collection unloaded, e.g. when called during pre-exit sync
        return
    cmd, action = url.split(":")
    conf = mw.col.decks.confForDid(self.card.odid or self.card.did)
    
    if action == "alert":
        play(ALERT_PATH)
        timeout = conf.get('autoAlert', 0)
        tooltip("Wake up! You have been looking at <br>"
                "the question for <b>{}</b> seconds!".format(timeout),
                period=1000)
    elif action == "action":
        action = conf.get('autoAction', "again")
    
    if action == "again":
        if self.state == "question":
            self._showAnswer()
        self._answerCard(1)
    elif action == "good":
        if self.state == "question":
            self._showAnswer()
        self._answerCard(self._defaultEase())
    elif action == "bury":
        mw.reviewer.onBuryCard()


Reviewer._linkHandler = wrap(Reviewer._linkHandler, linkHandler, "around")

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
Modifications to the Reviewer.
"""


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os

from aqt import mw
from aqt.reviewer import Reviewer
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


# html and timeouts
###############################################################################

button_html = """
<td id="spdfControls" width="50" align="center" valign="top" class="stat">
<span id="spdfTime" class="stattxt"></span><br>
<button title="Shortcut key: P"
    onclick="spdfClearCurrentTimeout();">More time!</button>
</td>
"""

script = """
var spdfAutoAlertTimeout = 0;
var spdfAutoAnswerTimeout = 0;
var spdfAutoActionTimeout = 0;
var spdfCurrentTimeout = null;
var spdfCurrentAction = null;
var spdfCurrentInterval = null;

function spdfReset() {
    clearInterval(spdfCurrentInterval);
    spdfCurrentTimeout = null;
    spdfCurrentAction = null;
}

function spdfUpdateTime() {
    var timeNode = document.getElementById("spdfTime");
    if (spdfTimeLeft === 0) {
        timeNode.textContent = "";
        return;
    }
    var time = Math.max(spdfTimeLeft, 0);
    var m = Math.floor(time / 60);
    var s = time %% 60;
    if (s < 10) {
        s = "0" + s;
    }
    timeNode.textContent = spdfCurrentAction + " " + m + ":" + s;
    spdfTimeLeft = time - 1;
};

function spdfSetCurrentTimer(timeout, action, ms) {
    spdfCurrentAction = action;
    spdfCurrentTimeout = timeout;
    spdfTimeLeft = Math.round(ms / 1000);
    spdfUpdateTime();
    spdfCurrentInterval = setInterval(function () {
        spdfUpdateTime();
    }, 1000);
}

function spdfClearCurrentTimeout() {
    if (spdfCurrentTimeout != null) {
        clearTimeout(spdfCurrentTimeout);
    }
    clearInterval(spdfCurrentInterval);
    var timeNode = document.getElementById("spdfTime");
    timeNode.textContent = "Stopped.";
}

function spdfSetAutoAlert(ms) {
    clearTimeout(spdfAutoAlertTimeout);
    spdfAutoAlertTimeout = setTimeout(function () { %(bridge)s("spdf:alert"); }, ms);
}

function spdfSetAutoAnswer(ms) {
    spdfReset();
    clearTimeout(spdfAutoAnswerTimeout);
    spdfAutoAnswerTimeout = setTimeout(function () { %(bridge)s('ans') }, ms);
    spdfSetCurrentTimer(spdfAutoAnswerTimeout, "Reveal", ms)
}
function spdfSetAutoAction(ms, action) {
    spdfReset();
    clearTimeout(spdfAutoActionTimeout);
    spdfAutoActionTimeout = setTimeout(function () { %(bridge)s("spdf:action"); }, ms);
    spdfSetCurrentTimer(spdfAutoActionTimeout, action, ms)
}

function spdfHide() {
    document.getElementById("spdfControls").style.display = "none";
}
function spdfShow() {
    document.getElementById("spdfControls").style.display = "";
}

document.getElementById("middle").insertAdjacentHTML("afterend", '%(button)s')
""" % (dict(bridge=JSPY_BRIDGE, button=button_html.replace("\n", "")))


def appendHTML(self, _old):
    return _old(self) + """<script>%s</script>""" % script


# set timeouts for auto-alert and auto-reveal
def setAnswerTimeouts(self):
    c = mw.col.decks.confForDid(self.card.odid or self.card.did)
    active = False
    if c.get('autoAnswer', 0) > 0:
        self.bottom.web.eval("spdfSetAutoAnswer(%d);" % (c['autoAnswer'] * 1000))
        active = True
    if c.get('autoAlert', 0) > 0:
        self.bottom.web.eval("spdfSetAutoAlert(%d);" % (c['autoAlert'] * 1000))
    if c.get("autoSkip") and c.get('autoAgain', 0) > 0:
        action = c.get('autoAction', "again").capitalize()
        self.bottom.web.eval("spdfSetAutoAction(%d, '%s');" %
                             (c['autoAgain'] * 1000, action))
        active = True
    
    if active:
        self.bottom.web.eval("spdfShow();")
    else:
        self.bottom.web.eval("spdfHide();")

# set timeout for auto-action


def setQuestionTimeouts(self):
    c = mw.col.decks.confForDid(self.card.odid or self.card.did)
    if not c.get("autoSkip") and c.get('autoAgain', 0) > 0:
        # keep "autoAgain" as name for legacy reasons
        action = c.get('autoAction', "again").capitalize()
        self.bottom.web.eval("spdfSetAutoAction(%d, '%s');" %
                             (c['autoAgain'] * 1000, action))
        self.bottom.web.eval("spdfShow();")
    else:
        self.bottom.web.eval("spdfHide();")


# clear timeouts for auto-alert and auto-reveal, run on answer reveal
def clearAnswerTimeouts():
    reviewer = mw.reviewer
    c = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)
    reviewer.bottom.web.eval("""
        if (typeof spdfAutoAnswerTimeout !== 'undefined') {
            clearTimeout(spdfAutoAnswerTimeout);
        }
        if (typeof spdfAutoAlertTimeout !== 'undefined') {
            clearTimeout(spdfAutoAlertTimeout);
        }
    """)
    if c.get("autoSkip"):
        reviewer.bottom.web.eval("""
            if (typeof spdfAutoActionTimeout !== 'undefined') {
                clearTimeout(spdfAutoActionTimeout);
            }
        """)

# clear timeout for auto-action, run on next card


def clearQuestionTimeouts():
    reviewer = mw.reviewer
    c = mw.col.decks.confForDid(reviewer.card.odid or reviewer.card.did)
    if not c.get("autoSkip"):
        mw.reviewer.bottom.web.eval("""
            if (typeof spdfAutoActionTimeout !== 'undefined') {
                clearTimeout(spdfAutoActionTimeout);
            }
        """)


# action handler
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


def initializeReviewer():
    Reviewer._linkHandler = wrap(Reviewer._linkHandler, linkHandler, "around")
    Reviewer._bottomHTML = wrap(Reviewer._bottomHTML, appendHTML, 'around')
    Reviewer._showAnswerButton = wrap(
        Reviewer._showAnswerButton, setAnswerTimeouts)
    Reviewer._showEaseButtons = wrap(Reviewer._showEaseButtons,
                                     setQuestionTimeouts)
    addHook("showAnswer", clearAnswerTimeouts)
    addHook("showQuestion", clearQuestionTimeouts)

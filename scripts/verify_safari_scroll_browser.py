#!/usr/bin/env python3
"""macOS Safari/WebKit history regression, including an inherited manual entry.

Requires the platform Safari WebDriver endpoint. The test drives an isolated
WebDriver browser session and never changes the user's Safari preferences.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

DRIVER=os.environ.get("SAFARI_DRIVER_URL", "http://127.0.0.1:9349")
ORIGIN=os.environ.get("SCROLL_TEST_ORIGIN", "https://fountain.coach")
CASES=[
    ("/essays/", ".essay-gallery-card:last-of-type a[href]"),
    ("/essays/the-composable-book/", '.essay-article p a[href*="governance"]'),
    ("/", '.estate-card.essay-entry a[href^="/essays/"]'),
]

def request(method: str, path: str, body=None):
    req=urllib.request.Request(
        DRIVER+path,
        data=None if body is None else json.dumps(body).encode(),
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r: result=json.load(r)
    except urllib.error.HTTPError as error:
        raise RuntimeError(error.read().decode()[:600]) from error
    payload=result.get("value", result)
    if isinstance(payload,dict) and "error" in payload:
        raise RuntimeError(json.dumps(payload))
    return payload

class Driver:
    def __init__(self):
        self.session=request("POST","/session",{"capabilities":{"alwaysMatch":{"browserName":"safari"}}})["sessionId"]
        self.path="/session/"+self.session
    def eval(self,script,*args):
        return request("POST",self.path+"/execute/sync",{"script":script,"args":list(args)})
    def visit(self,path):
        request("POST",self.path+"/url",{"url":ORIGIN+path})
    def back(self):
        request("POST",self.path+"/back",{})
    def refresh(self):
        request("POST",self.path+"/refresh",{})
    def wait(self,js,limit=12):
        start=time.monotonic()
        while time.monotonic()-start<limit:
            try:
                if self.eval("return "+js):return
            except (RuntimeError,urllib.error.URLError):pass
            time.sleep(.15)
        raise RuntimeError("wait timed out: "+js)
    def close(self):
        request("DELETE",self.path)

def main():
    d=Driver()
    try:
        # macOS Safari may retain the old manual setting across document
        # reloads. Verify the updated JS recovers that prior history entry.
        d.visit("/essays/the-composable-book/")
        d.wait('document.readyState==="complete"')
        state=d.eval("history.scrollRestoration='manual';return history.scrollRestoration")
        assert state=="manual",state
        d.refresh()
        d.wait('document.readyState==="complete"')
        time.sleep(.35)
        restored=d.eval("return history.scrollRestoration")
        assert restored=="auto",f"Safari retained a legacy manual entry after refresh: {restored}"
        print("SAFARI_MAC_LEGACY_ENTRY_RECOVERED auto",flush=True)
        for route,selector in CASES:
            d.visit(route)
            d.wait('document.readyState==="complete"')
            time.sleep(.3)
            before=d.eval("""
                const a=document.querySelector(arguments[0]);
                if(!a)throw Error("missing authored link "+arguments[0]);
                a.scrollIntoView({block:"center",behavior:"instant"});
                return {y:scrollY,mode:history.scrollRestoration,target:a.href};
            """,selector)
            d.eval("document.querySelector(arguments[0]).click();return true",selector)
            d.wait("location.href==="+json.dumps(before["target"]))
            d.back()
            d.wait("location.pathname==="+json.dumps(route))
            time.sleep(.6)
            after=d.eval("return {y:scrollY,mode:history.scrollRestoration}")
            delta=abs(before["y"]-after["y"])
            print("SAFARI_MAC_BACK",json.dumps({"route":route,"from":before,"to":after,"delta":delta}),flush=True)
            assert before["mode"]=="auto" and after["mode"]=="auto" and delta<=18, route
        print("SAFARI_MAC_BROWSER_HISTORY_ACCEPTED 1 legacy + 3 Back scenarios",flush=True)
    finally:
        d.close()

if __name__=="__main__":main()

<img src="nag.svg" height="200"/>

httpnag
=======
Maintain a database of HTTP heartbeats.

Why
---
1. I want to monitor the round trip latency from the internet to my home web
   server.
2. A friend wants to see how reliable his internet connection is.

Kill two birds with one script.

What
----
[httpnag.py](httpnag.py) is a Python 3 script that repeatedly issues a `HEAD`
request to an HTTP server and maintains a sqlite3 database of request/response
latency and the resulting responses.

How
---
```console
$ python3.7 httpnag.py --help
```

[httpnag.bat](httpnag.bat) is a Windows batch script that will launch
[httpnag.py](httpnag.py) using the no-UI version of the Python 3.7 executable.
**It expects Python to be installed at `C:\Program Files\Python37`**.

[httpnag.vbs](httpnag.vbs) is a Windows VBScript that executes
[httpnag.bat](httpnag.bat) without showing a command shell UI.

You can use the Windows task scheduler to run [httpnag.vbs](httpnag.vbs) on
system startup.  Make sure you configure the current working directory to be
this one (the same directory as the VBScript).

More
----
[histogram.sql](histogram.sql) is a sqlite3 script that prints an ASCII
histogram of HTTP request/response latencies.  The bins are in units of
milliseconds, in five-millisecond buckets.

For example,
```console
$ sqlite3 httpnag.sqlite <histogram.sql
Milliseconds  Bars
------------  ----------------------------------------------------------------------------------------------------
15.0          X'**'
20.0          X'**'
25.0          X'**'
30.0          X'**'
35.0          X'**************'
40.0          X'******'
45.0          X'******************'
50.0          X'******************************************'
55.0          X'****************************'
60.0          X'******************'
65.0          X'************************'
70.0          X'**********************************'
75.0          X'**************************************************************'
80.0          X'**********************************************************'
85.0          X'**********************************************************'
90.0          X'**************************************************************************************************
95.0          X'**************************************************************'
100.0         X'**************************************************************'
105.0         X'******************************************'
110.0         X'**********************************'
115.0         X'**************'
120.0         X'************************'
125.0         X'**'
130.0         X'**'
135.0         X'************'
140.0         X'******'
145.0         X'************'
150.0         X'**'
155.0         X'**'
205.0         X'**'
```

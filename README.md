---
Author: Jiayuan Zhang

Since: 03/11/2021

Version: 1.0

---
# CSC2031-Project
***
## A little message to the examiner
First I want to apologise that my lab report has 6 pages 
which is out of 4 pages limitation. I talked with the lecturer John 
in class and he generously admitted it. I do not mean it and I promise 
that I tried my best to simplify my report but I do not want to sacrifice the 
completeness. Please bear me with that, apologise for any inconvenience.
***
## Testing
All security requirements have been implemented in the system. 
Here I want to note three things: 
* You may notice that draw creation can be against some real life 
  lottery mechanism (details in the lab report). I did not implement 
  the solution (except the requirements in the `Secure Randomness` part) 
  for this issue but I gave a possible solution in the 
  `Evaluation` part of my report.
* **Recaptcha** feature has been implemented in the user login process.

* In the logging requirement, it requires that invalid access 
attempts should be logged, which is a little bit ambiguous. 
  To be clear with it, this system will log:
  * Unauthorised access attempt
    ```markdown
    For example, when an end user tries to access admin page or 
    the admin user tries to access lottery page through path traversal, 
    those activities will be logged into the log file.
    ```
  * Anonymous invalid access
    ```markdown
    For example, when an anonymous user tries to access profile pages, 
    that activity will be logged into the log file.
    ```
FROM python:latest
COPY Calc.py /home/Calc.py
COPY --chmod=755 testscript.py /home/testscript.py
ENTRYPOINT ["/usr/local/bin/python", "/home/testscript.py" ]
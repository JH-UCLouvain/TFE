#!/bin/python3
# Author : Jeremy Holodiline

from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from ipmininet.cli import IPCLI

import random

def store_feedback(grade, result, feedback):
    STORE = True
    if STORE:
        with open("tmp/student/feedback.txt", "w") as f:
            f.write(str(grade) + "\n")
            f.write(result + "\n")
            f.write(feedback)
    else:
        print(f"Grade : {grade}")
        print(f"Result : {result}")
        print(f"Feedback : {feedback}")

class MyTopology(IPTopo):

    def build(self, *args, **kwargs):

        switch_numbers = list(range(1,100))

        random_switch_number = random.choice(switch_numbers)
        a = self.addSwitch(f"s{random_switch_number}", prio=random_switch_number)
        switch_numbers.remove(random_switch_number)

        random_switch_number = random.choice(switch_numbers)
        b = self.addSwitch(f"s{random_switch_number}", prio=random_switch_number)
        switch_numbers.remove(random_switch_number)

        random_switch_number = random.choice(switch_numbers)
        c = self.addSwitch(f"s{random_switch_number}", prio=random_switch_number)
        switch_numbers.remove(random_switch_number)

        random_switch_number = random.choice(switch_numbers)
        d = self.addSwitch(f"s{random_switch_number}", prio=random_switch_number)
        switch_numbers.remove(random_switch_number)

        random_switch_number = random.choice(switch_numbers)
        e = self.addSwitch(f"s{random_switch_number}", prio=random_switch_number)
        switch_numbers.remove(random_switch_number)

        self.addLink(a, e)
        self.addLink(a, d)
        self.addLink(e, d)
        self.addLink(c, e)
        self.addLink(c, b)
        self.addLink(d, b)

        super(MyTopology, self).build(*args, **kwargs)

class Test:

    def __init__(self):
        self.n_test = 0
        self.n_success_test = 0
        self.feedback = ""
        self.correct_answer = []
        for s in net.switches:
            s_name = s.name
            lines = net[s_name].cmd(f"brctl showstp {s_name}").splitlines()
            for i in range(len(lines)):
                if "blocking" in lines[i]:
                    self.correct_answer.append(lines[i-1].split(" ")[0])
        if len(self.correct_answer) == 0: self.correct_answer.append(str("none"))
        else: self.correct_answer = sorted(list(set(self.correct_answer)))

    def blocking_port_test(self, student_answer):
        self.n_test += 1
        if student_answer == self.correct_answer:
            self.n_success_test += 1
            self.feedback += "Success\n"
        else:
            correst_str = ",".join(self.correct_answer)
            correst_str.rstrip(",")
            stud_str = ",".join(student_answer)
            stud_str.rstrip(",")
            self.feedback += f"Failed : the correct answer was {correst_str} but got {stud_str}\n"

    def send_feedback(self):
        grade = 100 if self.n_test == 0 else ((self.n_success_test / self.n_test) * 100)
        result = "success" if grade == 100 else "failed"
        store_feedback(grade, result, self.feedback)

student_answer = []

def answer(cli, args):
    global student_answer
    student_answer = sorted(list(set(args.split(","))))
    if student_answer == ['']: student_answer = [str("none")]

net = IPNet(topo=MyTopology())

try:
    net.start()

    IPCLI.do_answer = answer

    IPCLI(net)

    if len(student_answer) == 0: student_answer.append(str("none"))

    test = Test()
    test.blocking_port_test(student_answer)
    test.send_feedback()

except Exception as e:
    store_feedback(0, "crash", f"Error from the ipmininet script : {e}")

finally:
    net.stop()
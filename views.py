from flask import Blueprint, render_template
import csv


views = Blueprint(__name__, "views") #using this file to keep a list of views to be used by app

@views.route("/") #decorator to define the views of the website
def home(): #this is the home view
    return render_template("index.html")



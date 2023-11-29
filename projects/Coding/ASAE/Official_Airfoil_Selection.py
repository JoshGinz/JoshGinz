# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 19:48:53 2023

@author: Kvng_
"""

import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import math
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt

class Airfoil:
    def __init__(self, name, coordinates, performance_data=None, gif_link=None, reference=None):
        self.name = name
        self.coordinates = coordinates
        self.performance_data = performance_data if performance_data else {}
        self.gif_link = gif_link
        self.reference = reference

def compute_performance_data(coordinates, weight, length, wingspan, speed, alpha):
    AR = wingspan**2 / (wingspan * length)  # Aspect Ratio corrected
    e = 0.85  # Oswald efficiency factor

    # Extracting some properties from coordinates to introduce variability
    max_thickness = max([y for _, y in coordinates])
    camber = (max_thickness - min([y for _, y in coordinates])) / 2
    leading_edge_slope = (coordinates[1][1] - coordinates[0][1]) / (coordinates[1][0] - coordinates[0][0])
    
    # Coefficient of Lift (before stall)
    alpha_rad = alpha * (3.14159 / 180)
    max_cl = 2 * 3.14159 * alpha_rad * (1 + leading_edge_slope) if alpha < 15 else 1.5
    
    # Required Coefficient of Lift for level flight
    rho = 1.225  # air density at sea level in kg/m^3
    wing_area = wingspan * length
    required_cl = (2 * weight) / (rho * speed**2 * wing_area)
    
    # Coefficient of Drag
    CD0 = 0.025 + 0.005 * camber
    max_cd = CD0 + (max_cl**2) / (3.14159 * e * AR)
    
    # Lift to Drag ratio
    ld_ratio = max_cl / max_cd

    # Reynolds number (rough estimation, assuming kinematic viscosity for air at sea level)
    Re = speed * wingspan / 1.46e-5

    # Mach number (assuming speed of sound as 343 m/s)
    Mach = speed / 343

    return {
        "max_cl": max_cl, 
        "required_cl": required_cl,
        "max_cd": max_cd, 
        "ld_ratio": ld_ratio, 
        "Re": Re, 
        "Mach": Mach
    }


def process_airfoil(args):
    link, weight, length, wingspan, speed, alpha = args
    try:
        dat_url = 'https://m-selig.ae.illinois.edu/ads/' + link['href']
        print(f"Processing {dat_url}...")

        # Extracting the coordinates
        dat_response = requests.get(dat_url)
        dat_lines = dat_response.text.splitlines()
        name_description = dat_lines[0]
        
        # Attempt to extract coordinates, catch any ValueError
        try:
            coordinates = [tuple(map(float, line.split())) for line in dat_lines[1:] if len(line.split()) == 2]
        except ValueError as e:
            print(f"Error processing {dat_url}: {e}")
            return None

        # Performance data
        performance_data = compute_performance_data(coordinates, weight, length, wingspan, speed, alpha)
        
        # Enrichment
        gif_link = None
        ref = None
        
        # Extracting the .gif link if it exists
        gif_tag = link.find_next_sibling('a', href=True, text=True)
        if gif_tag and '.gif' in gif_tag['href']:
            gif_link = 'https://m-selig.ae.illinois.edu/ads/' + gif_tag['href']
            
        # Extracting the reference if it exists
        if "Ref" in link.parent.text:
            ref = link.parent.text.split("Ref")[1].strip()

        # Creating enriched airfoil object
        airfoil = Airfoil(name_description, coordinates, performance_data)
        airfoil.gif_link = gif_link
        airfoil.reference = ref
        
        return airfoil
    
    except Exception as e:
        print(f"Error processing {dat_url}: {e}")
        return None

import matplotlib.pyplot as plt

def plot_airfoil(airfoil):
    x_coords, y_coords = zip(*airfoil.coordinates)
    plt.figure(figsize=(10,5))
    plt.plot(x_coords, y_coords, '-o', markersize=2)
    plt.title(airfoil.name)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def analyze_airfoils(weight, length, wingspan, speed, alpha):
    BASE_DIRECTORY_URL = 'https://m-selig.ae.illinois.edu/ads/coord_database.html'
    response = requests.get(BASE_DIRECTORY_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    airfoil_links = [link for link in soup.find_all('a', href=True) if '.dat' in link['href']]
    
    args_list = [(link, weight, length, wingspan, speed, alpha) for link in airfoil_links]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        airfoils = list(filter(None, executor.map(process_airfoil, args_list)))

    return airfoils

def evaluate_best_airfoil(args_list):
    best_score = float('-inf')
    best_airfoil = None

    for args in args_list:
        airfoil_data = process_airfoil(args)
        
        # Skip if airfoil_data is None
        if airfoil_data is None:
            continue

        score = compute_score(airfoil_data)
        if score > best_score:
            best_score = score
            best_airfoil = airfoil_data
            # Update UI with the current best airfoil
            results_text.delete(1.0, tk.END)
            results_text.insert(tk.END, f"Current Best: {best_airfoil.name}: L/D ratio: {best_airfoil.performance_data['ld_ratio']:.2f}, Cl: {best_airfoil.performance_data['max_cl']:.2f}, Cd: {best_airfoil.performance_data['max_cd']:.2f}\n")
    
    return best_airfoil


def compute_score(airfoil_data):
    return airfoil_data.performance_data['ld_ratio']

def fetch_image_url(query):
    """Fetches the first image URL from Google Custom Search for a given query."""
    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'num': 1,
        'start': 1,
        'imgSize': 'large',
        'searchType': 'image',
        'key': 'AIzaSyBimN8eyJFfvdSTFwqLqhu1ffz98Y8J2vY',
        'cx': 'd1935a3788cd9411b'
    }

    response = requests.get(endpoint, params=params).json()
    try:
        return response['items'][0]['link']
    except KeyError:
        return None

def display_best_airfoil_info(airfoil):
    # Image
    airfoil_name = airfoil.name.split(' ')[0]  # Extracting the first word from the name as it's likely the model
    image_url = fetch_image_url(airfoil_name)
    plot_airfoil(airfoil)
    if image_url:
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo
    else:
        image_label.config(image='')
    
    # Description
    description_text.delete(1.0, tk.END)
    description_text.insert(tk.END, airfoil.reference if airfoil.reference else "No description available.")


def on_submit():
    weight = float(weight_entry.get())
    length = float(length_entry.get())
    wingspan = float(wingspan_entry.get())
    speed = float(speed_entry.get())
    alpha = float(alpha_entry.get())
    
    # Generate args_list for all the airfoils
    BASE_DIRECTORY_URL = 'https://m-selig.ae.illinois.edu/ads/coord_database.html'
    response = requests.get(BASE_DIRECTORY_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    airfoil_links = [link for link in soup.find_all('a', href=True) if '.dat' in link['href']]
    args_list = [(link, weight, length, wingspan, speed, alpha) for link in airfoil_links]

    # Evaluate the best airfoil from all the candidates
    best_airfoil = evaluate_best_airfoil(args_list)

    # Display the final result (this will overwrite the intermediate results)
    results_text.delete(1.0, tk.END)
    results_text.insert(tk.END, f"Best Airfoil: {best_airfoil.name}: L/D ratio: {best_airfoil.performance_data['ld_ratio']:.2f}, Cl: {best_airfoil.performance_data['max_cl']:.2f}, Cd: {best_airfoil.performance_data['max_cd']:.2f}\n")
    display_best_airfoil_info(best_airfoil)


root = tk.Tk()
root.title("Airfoil Analyzer")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Weight:").grid(column=0, row=0, sticky=tk.W)
weight_entry = ttk.Entry(frame)
weight_entry.grid(column=1, row=0)

ttk.Label(frame, text="Length:").grid(column=0, row=1, sticky=tk.W)
length_entry = ttk.Entry(frame)
length_entry.grid(column=1, row=1)

ttk.Label(frame, text="Wingspan:").grid(column=0, row=2, sticky=tk.W)
wingspan_entry = ttk.Entry(frame)
wingspan_entry.grid(column=1, row=2)

ttk.Label(frame, text="Speed:").grid(column=0, row=3, sticky=tk.W)
speed_entry = ttk.Entry(frame)
speed_entry.grid(column=1, row=3)

ttk.Label(frame, text="Alpha:").grid(column=0, row=4, sticky=tk.W)
alpha_entry = ttk.Entry(frame)
alpha_entry.grid(column=1, row=4)

submit_btn = ttk.Button(frame, text="Analyze Airfoils", command=on_submit)
submit_btn.grid(column=0, row=5, columnspan=2, pady=10)

results_text = tk.Text(frame, width=50, height=10)
results_text.grid(column=0, row=6, columnspan=2, pady=10)

# Label to display the image of the best airfoil
image_label = ttk.Label(frame)
image_label.grid(column=0, row=7, columnspan=2, pady=10)

# Text widget to display the description/reference of the best airfoil
description_text = tk.Text(frame, width=50, height=5)
description_text.grid(column=0, row=8, columnspan=2, pady=10)

root.mainloop()

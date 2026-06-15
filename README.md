# Running Dinner Optimizer

A system to automate participant assignment and route optimization for a recurring **Running Dinner** event.
Tailored for the swimming team of RWTH Aachen Hochschulsport.

This project combines **optimization (MILP)** with a **desktop GUI** to generate efficient, real-world dinner routes while respecting event constraints.

---

## Overview

A *Running Dinner* is a social event where participants visit multiple locations (e.g., starter, main course, dessert) throughout the evening. Organizing such an event manually is complex due to:

- Travel distances between participants
- Group assignment constraints
- Avoiding repeated pairings
- Balancing hosts and guests

This project automates the entire process using **optimization techniques** and provides a **user-friendly interface** to manage participants and visualize results.

---

## Features

- **Automatic participant assignment**
- **Route optimization** minimizing total travel distance
- **Constraint handling**, including:
  - Each participant attends all courses
  - Balanced hosting responsibilities
  - No repeated group pairings
- **Desktop GUI (PySide6)** for:
  - Managing participants
  - Running optimization
  - Viewing results
- **Geocoding integration** for real-world distance calculations

---

## How It Works

The core of the system is a **Mixed-Integer Linear Programming (MILP)** model.

### Objective
Minimize total travel distance across all participants.

### Constraints (examples)
- Each participant is assigned to exactly one group per course
- Hosting responsibilities are distributed fairly
- Participants do not meet the same group more than once
- Capacity constraints per location

The optimization model is solved using a linear solver (HiGHS).

---

## Tech Stack

- **Python**
- **Optimization:** MILP 
- **GUI:** PySide6 (Qt)
- **Geocoding / Distance:** External APIs 

---

## Installation

```bash
git clone https://github.com/jalapawa/Running-Dinner-Optimizer.git
cd Running-Dinner-Optimizer
pip install -r requirements.txt
```
## Usage
```
python app.py
```
- Import particpant table (format can be adapted in the code)
- Choose your settings

## To-Dos
- Changable table format
- Route visualization
- Automatic Email distribution

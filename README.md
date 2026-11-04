# LOOP - Live Object-Oriented Playground

An interactive Python OOP visualizer that uses scenario-based simulations to make object-oriented programming concepts visible during execution.

## Live Demo

[Launch LOOP](https://loop-duzg.onrender.com/)

> Note: The free hosting service may take a short time to wake up on the first load.

## Overview

LOOP (Live Object-Oriented Playground) is an interactive Python OOP visualizer designed to make object-oriented programming easier to understand through visual execution.

Learners read the real Python source of a scenario and click a method to run it. As the code executes, LOOP highlights each line, lights up the method calls between objects, shows how object state changes, and explains every step in plain language.

Scenarios are example contexts for the same OOP ideas, and new scenarios can be added without changing the playground. The current version includes three:

| Scenario | Actors | What it shows best |
| --- | --- | --- |
| Cybersecurity | Attacker, Device, Victim | Inheritance, overriding, `super()`, abstraction and polymorphism |
| Library | Member, Library | Separate objects of one class, object references, delegation, properties and encapsulation |
| Smart Home | Resident, Home Hub, Devices | Polymorphism, overriding versus inherited methods, `super()` and guarded methods |

## Goals

- Make Python OOP concepts easier to understand visually
- Clearly distinguish classes from object instances
- Show method calls, object interactions, and state changes during execution
- Demonstrate encapsulation, inheritance, `super()`, polymorphism, abstraction, and object relationships
- Keep Python as the source of truth: everything shown comes from real execution

## Features

- Real Python execution through FastAPI, traced line by line
- The genuine Python source, fully visible inside the actor panels
- Click a method in the code to run an action
- Highlighting of the running line, and of methods waiting in the call stack
- Animated circuit routes between methods, including `super()` calls
- Status icons showing each object's state, kept between actions
- A Terminal explaining each step: the story, the code, and the OOP concept
- Play, Pause, Previous, Next, Replay, and Reset controls
- Scenario tabs, with scenarios added as separate folders and their own actor colours

## Run Locally

Requires Python 3.11 or newer.

```bash
python -m pip install -r requirements.txt
python -m uvicorn api:app --reload
```

Open **http://127.0.0.1:8000**.

## Scope

### In Scope

- Scenario-based OOP demonstrations using real Python execution
- Line-by-line source highlighting and call visualization
- Object state tracking and beginner-friendly explanations
- Adding new scenarios without changing the playground

### Out of Scope

- Real cybersecurity attacks or network access
- Real malware, ransomware, or interception
- A general-purpose Python debugger, interpreter, or code editor

## Technology Stack

| **Technology** | **Purpose** |
| --- | --- |
| Python | Educational OOP classes, execution tracing, and scenario management |
| FastAPI | Backend API connecting Python to the browser |
| JavaScript | Rendering, playback, circuits, and interaction |
| HTML | Interface structure |
| CSS | Layout, highlighting, and animations |

## Documentation

Original (V1): [P03-LOOP.pdf](P03-LOOP.pdf)

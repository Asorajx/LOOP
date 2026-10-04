# LOOP - Live Object-Oriented Playground

An interactive Python OOP visualizer that uses scenario-based simulations to make object-oriented programming concepts visible during execution.

## Live Demo

[Launch LOOP](https://loop-duzg.onrender.com/)

> Note: The free hosting service may take a short time to wake up on the first load.

## Overview

LOOP (Live Object-Oriented Playground) is an interactive Python OOP visualizer designed to make object-oriented programming easier to understand through visual execution.

The current version uses a fictional cybersecurity scenario containing attackers, network devices, connections, and defenders. As Python methods execute, LOOP visualizes method calls, object interactions, state changes, inheritance, and the corresponding source code in real time.

## Goals

- Make Python OOP concepts easier to understand visually
- Clearly distinguish classes from object instances
- Show method calls, object interactions, and state changes during execution
- Demonstrate encapsulation, inheritance, composition, abstraction, and polymorphism
- Keep Python as the source of truth for simulation state

## Features

- Manual and Guided simulation modes
- Real Python execution through FastAPI
- Six fictional attack types
- Defensive actions including block, isolate, restore, and secure
- Real Python source-code display and highlighting
- Object-instance indicators such as `DEV001`, `DEV002`, and `CON001`
- Animated interaction paths
- Real before-and-after state changes
- Terminal execution history with OOP explanations
- Visual inheritance and `super()` calls
- Previous, Next, Play, Pause, Replay, and Reset controls

## OOP Concepts Demonstrated

- **Encapsulation** - objects manage their own internal state through methods
- **Composition** - the simulation contains attackers, defenders, devices, and connections
- **Abstraction** - `Attack` defines a common `execute()` interface
- **Polymorphism** - different attack classes implement the same `execute()` method
- **Inheritance** - `DDoSAttack` extends `DoSAttack`, while `RansomwareAttack` extends `MalwareAttack`
- **Method Overriding** - child classes provide their own implementation of `execute()`
- **`super()`** - child classes reuse behaviour from their parent classes

## Scope

### In Scope

- Manual and Guided simulation modes
- Six fictional attack types and defensive actions
- Interactive Python source-code display
- Object-instance and state-change visualization
- Inheritance and `super()` visualization
- Execution history and OOP explanations

### Out of Scope

- Real cybersecurity attacks or network access
- Real malware, ransomware, phishing, or DoS activity
- Password cracking or vulnerability scanning
- Real firewall or antivirus integration
- Full Python debugger or interpreter-level tracing

## Technology Stack

| **Technology** | **Purpose** |
| --- | --- |
| Python | OOP classes, simulation logic, object state, and tracing |
| FastAPI | Backend API connecting Python to the browser |
| JavaScript | User interaction, playback, and visualization |
| HTML | Interface structure |
| CSS | Layout, highlighting, animations, and effects |

## Documentation

Full project report: `P03-LOOP.pdf`

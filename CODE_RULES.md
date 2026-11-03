# LOOP Code Rules

Guidelines for anyone working on LOOP, including AI coding assistants.
LOOP exists to help beginners **see real Python OOP code run**. When a rule
here conflicts with adding a feature, the rule wins.

## 1. Terminology

Use these words consistently in code, UI text, and documentation.

| Term | Meaning |
| --- | --- |
| **Playground** | The complete interactive simulation environment. |
| **Scenario** | The context OOP is shown in, such as Cybersecurity. |
| **Action** | Something the user chooses to do within a scenario. |
| **Actor panel** | A group of related classes, showing their real Python code. Defined by the scenario. |
| **Code display** | The real Python source inside the actor panels, with the executing line highlighted. |
| **Terminal** | The output explaining each step: storyboard, code explanation, OOP concept. |
| **Route Indicators** | The circuit network between methods, and the travelling light on the live call. |

## 2. Educational Python code

Scenario classes are what beginners read. Every line must earn its place.

- Keep methods short. Most should be one to four lines.
- Use short, meaningful names: `device`, `connection`, `infected`, `attack`, `recover`.
  Avoid abbreviations (`dev`, `conn`, `atk`) and long technical names (`increase_risk_level_by_amount`).
- Avoid unnecessary conditionals, helper methods, and type checks such as `hasattr`.
- No tracing, logging, serialisation, or web code inside educational classes.
- No comments that repeat the code. The Terminal does the explaining.
- Do not remove an OOP concept (inheritance, `super()`, overriding, encapsulation,
  polymorphism, abstraction, object relationships) just to shorten code.

```python
# Good
class RansomwareAttack(MalwareAttack):
    def execute(self, target):
        super().execute(target)
        target.lock_files()

# Bad: tracing and bookkeeping hide the idea
class RansomwareAttack(MalwareAttack):
    def execute(self, target):
        if self.tracer is not None:
            self.tracer.method_started(self.name, "RansomwareAttack", "execute", target.device_id)
        super().execute(target)
        ...
```

- Prefer one clear example per concept over several that teach the same thing.
  Before adding a class or method, check which concept it demonstrates that isn't
  already covered, and remove supporting state that no remaining action uses.
- Objects should change their own state through methods (`target.infect()`), so the
  call is visible as a circuit route and the encapsulation lesson stays true.

## 3. Accuracy

Explanations must describe what Python actually does.

- `_name` is a convention meaning "internal". `__name` triggers name mangling.
  Neither makes an attribute truly private. Never call them private.
- `super().method()` runs the parent implementation only because the child calls it,
  on the **same** object. Inheritance does not run parent methods automatically.
- Overriding replaces a parent method unless the child calls `super()`.
- Polymorphism needs a caller that uses a shared interface (for example
  `attack.execute(target)`) without knowing the concrete class. Do not label a direct call as polymorphism.
- An object that stores a reference to an independently created object is an
  **association**, not composition.
- Link to the official Python documentation (`docs.python.org`) for further reading.

## 4. Storyboards must match executed code

A storyboard may only describe behaviour the code really performs. If the story
says "Device A goes offline", some executed line must set that state.

Keep stories short, plain cause and effect, using the names learners see
("Attacker", "Victim", "Device A"), not invented characters or jargon:

```python
"Attacker sends malware to {target}."         # good
"Mallory deploys a polymorphic payload ..."   # bad: made-up name, jargon
```

## 5. Actions start from the code

Each action names the def line that starts it (`"method": "MalwareAttack.execute"`).
Clicking that line in the Playground runs the action's full call, such as
`attacker.launch(malware, target)`, never the clicked method on its own.
Constructors, abstract methods and helpers are not actions. Give each def line
at most one action.

## 6. Tracing and source display

- The engine observes scenario code from outside (`sys.settrace`). Scenario classes never call the tracer.
- The actor panels show each class's **genuine, complete source**, fully expanded, exactly as
  it appears in the file. Never show rewritten copies, and don't hide or collapse lines.
- Highlight lines using real file line numbers from the trace, never by searching for text.
- Interface labels (object IDs, status icons) sit above a class's code, never between its lines.
- Explanations are keyed to real methods and lines. Tests must fail if a key no longer matches the source.
- Circuit routes come from real execution: the engine discovers them by running every action
  on fresh objects, and the browser adds any new route a live run uses. Never hardcode routes.
  Only the call happening at the current step lights up.

## 7. Directory structure

Keep it shallow. Shared infrastructure and scenarios stay separate.

```
api.py                    FastAPI app and sessions (uvicorn api:app)
engine/
  tracer.py               records calls, lines and state changes
  source.py               reads genuine source and line numbers
  scenario_manager.py     finds scenarios, runs actions, discovers routes
scenarios/
  cybersecurity/
    attacks.py            educational classes
    devices.py
    victim.py
    scenario.py           builds objects, lists actor panels, actions and status icons
    story.py              storyboard, code, and concept text
web/                      shared frontend: index.html, css/, js/, images/
tests/
```

- Each scenario lives in its own self-contained folder: its classes, setup, actions, and explanations.
- The engine, API, and frontend must not hardcode scenario details such as
  "Attacker", "DEV001", or attack names. They read them from the scenario.
- To add a scenario, add a folder. Do not copy the engine or the frontend.

## 8. Formatting and comments

Comments explain **why** something works the way it does, or how less obvious behaviour
works. Don't describe what a line already says.

```js
/* Circuit positions depend on where the method rows sit. */
/* Redraw when the panels change size. */
```

- **JS and CSS:** use `/* Sentence. */` comments. For longer explanations, use several
  single-line comments in a row, not one comment spread over several lines with `*`.
- **Major sections** in JS and CSS use this header, with two blank lines above and one below:

  ```js
  /* =========================
     Section Name
     ========================= */
  ```

  In HTML, use the same shape with `<!-- ... -->`. Use headers only for real sections
  (helpers, playback, circuits, event listeners, layout, responsive), never inside functions.
- **Normal comments:** one blank line above, none below, so the comment stays with its code.
  A comment that opens a block (straight after `{`) needs no blank line above.
- **HTML:** comment only where something isn't obvious, such as content filled in by scripts.
- **Python:** use `#` comments and docstrings as usual.
- Keep related code together: a component's variables, functions and event listeners in one
  section, and a component's CSS selectors next to each other.
- CSS properties go roughly in this order: layout and position, size, background, spacing,
  typography, borders, effects, interaction, animation. Don't reorder working CSS just for this.

## 9. Keep it simple

- Prefer one clear file over several tiny ones. Avoid deep nesting.
- No frameworks, plugin systems, or abstractions until a second real use needs them.
- Only remove code once you've confirmed nothing uses it. Search the whole project,
  including class names built in JS template strings, before deleting CSS or functions.
- Describe each new interface element by what it helps a beginner understand. If it does not help, leave it out.
- Match the style of the surrounding code.
- A cleanup must not change behaviour or appearance. Anything that might belongs in a
  separate, reviewed change.

## 10. Before you finish a change

- `python -m pytest -q` passes.
- Each action still runs, and the actor method, route indicator, highlighted line,
  and Terminal step stay in sync while stepping forward and back.
- New or changed explanations are accurate per section 3.
- Someone unfamiliar with LOOP could understand the change.

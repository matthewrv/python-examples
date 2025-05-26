# Python by Example 🐍

A collection of small Python code snippets demonstrating important (and sometimes surprising) behaviors of the language and libraries I use.

## 🚀 Getting Started

### Setting Up the Environment

- **NixOS users** (like me 😉): Simply run `nix-shell`, and you’re ready to explore Python’s intricacies.
- **Other systems**: Use `uv` to configure the project:

  ```bash
  uv sync
  ```

  After this, you should be good to go!

### Running Examples

Browse the `examples/` directory (organized by topic), read the commented code to understand what each script does, and run it with Python. For example:

```bash
python examples/threads/sql_alchemy_is_not_thread_safe.py
```

Happy coding! 🎉

## 📑 Index

### builtins
- [booleans_are_integers](./examples/builtins/booleans_are_integers.py) - Demonstrates how Python booleans are actually a subtype of integers
- [round_is_not_math_round](./examples/builtins/round_is_not_math_round.py) - Shows that Python's default rounding uses banker's rounding (round-to-even) rather than standard mathematical rounding

### functions
- [default_mutable_args_are_bad](./examples/functions/default_mutable_args_are_bad.py) - Illustrates unexpected behavior when using mutable data structures as default function arguments

### threads
- [race_conditions.py](./examples/threads/race_conditions.py) - Demonstrates race condition prevention during deque insertion (using a practical example)
- [sql_alchemy_session_is_not_thread_safe.py](./examples/threads/sql_alchemy_session_is_not_thread_safe.py) - Shows a race condition that can occur with SQLAlchemy sessions due to their thread-unsafe nature

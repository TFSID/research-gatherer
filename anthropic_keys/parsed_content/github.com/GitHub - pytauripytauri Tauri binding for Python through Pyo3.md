---
source: https://github.com/pytauri/pytauri
parsed_date: 2026-06-27 01:30:06
domain: github.com
---

Title: GitHub - pytauri/pytauri: Tauri binding for Python through Pyo3

URL Source: https://github.com/pytauri/pytauri

Markdown Content:
[![Image 1: banner.png](https://raw.githubusercontent.com/pytauri/branding/6832e0defd4220b8a3f5c1f111bd164cee616bbe/assets/banner.png)](https://raw.githubusercontent.com/pytauri/branding/6832e0defd4220b8a3f5c1f111bd164cee616bbe/assets/banner.png)

[Tauri](https://github.com/tauri-apps/tauri) bindings for Python through [Pyo3](https://github.com/PyO3/pyo3)

* * *

[![Image 2: CI: docs](https://github.com/pytauri/pytauri/actions/workflows/docs.yml/badge.svg)](https://github.com/pytauri/pytauri/actions/workflows/docs.yml)[![Image 3: msrv](https://camo.githubusercontent.com/2cb5328b9f046ff32ed53918ba24bf684433777a68494c5adcc95502cb45f1da/68747470733a2f2f696d672e736869656c64732e696f2f6372617465732f6d7372762f707974617572693f6c6f676f3d72757374)](https://rust-lang.github.io/rfcs/2495-min-rust-version.html)[![Image 4: requires-python](https://camo.githubusercontent.com/aab7ee2d1b3b9dfca97cfee6a912a1d1505e83aaa27fe24dc66ee578b67c02b5/68747470733a2f2f696d672e736869656c64732e696f2f707974686f6e2f72657175697265642d76657273696f6e2d746f6d6c3f746f6d6c46696c65506174683d68747470732533412532462532467261772e67697468756275736572636f6e74656e742e636f6d25324670797461757269253246707974617572692532467265667325324668656164732532466d61696e253246707974686f6e25324670797461757269253246707970726f6a6563742e746f6d6c266c6f676f3d707974686f6e)](https://packaging.python.org/en/latest/specifications/core-metadata/#requires-python)[![Image 5: Discord](https://camo.githubusercontent.com/4741dfa0485e2beb228da8814924ab56c3ba05e03f3238e2159eebf515e5e842/68747470733a2f2f696d672e736869656c64732e696f2f646973636f72642f313431313334393735363230323138383934323f6c6f676f3d646973636f7264266c6162656c3d646973636f7264)](https://discord.gg/TaXhVp7Shw)

Documentation: [https://pytauri.github.io/pytauri/](https://pytauri.github.io/pytauri/)

Source Code: [https://github.com/pytauri/pytauri/](https://github.com/pytauri/pytauri/)

* * *

This is a completely free and open-source project, but it is difficult to maintain without incentives and contributions from the community.

If you think this project is helpful, consider giving it a star [![Image 6: GitHub Repo stars](https://camo.githubusercontent.com/91764e28d6c5969632f116780ae1da1b28403aa8fe86046031e40affb90dd2ce/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f73746172732f707974617572692f707974617572693f7374796c653d736f6369616c)](https://github.com/pytauri/pytauri), it would be very helpful for my work and studies. 🥺👉👈

* * *

## Features

[](https://github.com/pytauri/pytauri#features)
> **TL;DR**
> 
> 
> You are hurry and just wanna see/run the demo? See [examples/tauri-app](https://github.com/pytauri/pytauri/tree/main/examples/tauri-app).

*   Need Rust compiler, but **almost don't need to write Rust code**!

*   Or use `pytauri-wheel`, **you won't need the Rust compiler, everything can be done in Python**! Check out [examples/tauri-app-wheel](https://github.com/pytauri/pytauri/tree/main/examples/tauri-app-wheel).

*   Can be integrated with `tauri-cli` to build and package standalone executables!

    *   Use `Cython` to protect your source code!

*   No IPC (inter-process communication) overhead, secure and fast, thanks to [Pyo3](https://github.com/PyO3/pyo3)!

*   Support Tauri official plugins(e.g., [notification](https://docs.rs/tauri-plugin-notification/latest/tauri_plugin_notification/)), and you can write your own plugins!

[![Image 7: demo](https://private-user-images.githubusercontent.com/126865849/377129140-14ad5b51-b333-4d80-b04b-af72c4179571.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDUsIm5iZiI6MTc4MjQ5ODYwNSwicGF0aCI6Ii8xMjY4NjU4NDkvMzc3MTI5MTQwLTE0YWQ1YjUxLWIzMzMtNGQ4MC1iMDRiLWFmNzJjNDE3OTU3MS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjI2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNlQxODMwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03NzU0NjU3OGZmOTc3YTRkZWI1NTI1NDQ0NjFiZjdlNWZlYzY3NjliNGQ5ODdjMzJlMmNkOTE0OWU4Yjg0NDVmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZnaWYifQ.km0y1Hn0IbXpWIpsgssSWQ6RM2ppgMfytg59GAosCs0)](https://private-user-images.githubusercontent.com/126865849/377129140-14ad5b51-b333-4d80-b04b-af72c4179571.gif?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3ODI0OTg5MDUsIm5iZiI6MTc4MjQ5ODYwNSwicGF0aCI6Ii8xMjY4NjU4NDkvMzc3MTI5MTQwLTE0YWQ1YjUxLWIzMzMtNGQ4MC1iMDRiLWFmNzJjNDE3OTU3MS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjYwNjI2JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNlQxODMwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT03NzU0NjU3OGZmOTc3YTRkZWI1NTI1NDQ0NjFiZjdlNWZlYzY3NjliNGQ5ODdjMzJlMmNkOTE0OWU4Yjg0NDVmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZyZXNwb25zZS1jb250ZW50LXR5cGU9aW1hZ2UlMkZnaWYifQ.km0y1Hn0IbXpWIpsgssSWQ6RM2ppgMfytg59GAosCs0)

*   Natively support async python (`asyncio`, `trio` or `anyio`)

*   **100%**[Type Completeness](https://microsoft.github.io/pyright/#/typed-libraries?id=type-completeness)

*   Ergonomic API (and as close as possible to the Tauri Rust API)

    *   [Automatically generated TypeScript types and client for IPC](https://github.com/pytauri/pytauri/tree/main/examples/tauri-app/src/client)

    *   Python

import sys

from pydantic import BaseModel
from pytauri import (
    AppHandle,
    Commands,
)
from pytauri_plugins.notification import NotificationExt

commands: Commands = Commands()

class Person(BaseModel):
    name: str

class Greeting(BaseModel):
    message: str

@commands.command()
async def greet(body: Person, app_handle: AppHandle) -> Greeting:
    notification_builder = NotificationExt.builder(app_handle)
    notification_builder.show(title="Greeting", body=f"Hello, {body.name}!")

    return Greeting(
        message=f"Hello, {body.name}! You've been greeted from Python {sys.version}!"
    ) 
    *   Frontend

import { pyInvoke } from "tauri-plugin-pytauri-api";
// or: `const { pyInvoke } = window.__TAURI__.pytauri;`

export interface Person {
    name: string;
}

export interface Greeting {
    message: string;
}

export async function greet(body: Person): Promise<Greeting> {
    return await pyInvoke("greet", body);
} 

*   Can be integrated with [nicegui](https://github.com/zauberzeug/nicegui)/[gradio](https://github.com/gradio-app/gradio)/[FastAPI](https://github.com/fastapi/fastapi) to achieve a full-stack Python development experience (i.g., without `Node.js`). See [examples/nicegui-app](https://github.com/pytauri/pytauri/tree/main/examples/nicegui-app).

## Release

[](https://github.com/pytauri/pytauri#release)
We follow [Semantic Versioning 2.0.0](https://semver.org/).

Rust and its Python bindings, PyTauri core and its plugins will keep the same `MAJOR.MINOR` version number.

| name | pypi | crates.io | npmjs |
| --- | --- | --- | --- |
| 👉 **core** | - | - | - |
| pytauri | [![Image 8: pytauri-pypi-v](https://camo.githubusercontent.com/3a944d9cad8bbe60c58bda4fda2c215b7a3cd98f1c0095c944d74995134e98e5/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f70797461757269)](https://pypi.org/project/pytauri) | [![Image 9: pytauri-crates-v](https://camo.githubusercontent.com/663842750719b9d46be9948d337a393ed38e4c09a49aaf111cd41ab7f78c9cc5/68747470733a2f2f696d672e736869656c64732e696f2f6372617465732f762f70797461757269)](https://crates.io/crates/pytauri) |  |
| pytauri-core |  | [![Image 10: pytauri-core-crates-v](https://camo.githubusercontent.com/3e0c71cfa8a21f996f738964328610581944a009a704a788f45dfc1ff101746c/68747470733a2f2f696d672e736869656c64732e696f2f6372617465732f762f707974617572692d636f7265)](https://crates.io/crates/pytauri-core) |  |
| tauri-plugin-pytauri |  | [![Image 11: tauri-plugin-pytauri-crates-v](https://camo.githubusercontent.com/ebc201f27e3102b59dc03a2e18b44c340b610ab6c834b96f212ac7733c074e62/68747470733a2f2f696d672e736869656c64732e696f2f6372617465732f762f74617572692d706c7567696e2d70797461757269)](https://crates.io/crates/tauri-plugin-pytauri) | [![Image 12: tauri-plugin-pytauri-api-npm-v](https://camo.githubusercontent.com/973e3c2f7708726a05e04894f385d3f884ada6c7777dad0b3a325e61f805ca6b/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f74617572692d706c7567696e2d707974617572692d617069)](https://www.npmjs.com/package/tauri-plugin-pytauri-api) |
| 👉 **wheel** | - | - | - |
| pytauri-wheel | [![Image 13: pytauri-wheel-pypi-v](https://camo.githubusercontent.com/5d11911fe09e06166b934d78a5ea7ebea8fd73dc31d00dd81e9883d2ee8efad7/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f707974617572692d776865656c)](https://pypi.org/project/pytauri-wheel) |  |  |
| 👉 **utils** | - | - | - |
| pyo3-utils | [![Image 14: pyo3-utils-pypi-v](https://camo.githubusercontent.com/a29cd3977eb9aad7a0568cf2a3fb4b48ed721122f06df4cf9c2d053d7e1dedfc/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f70796f332d7574696c73)](https://pypi.org/project/pyo3-utils) | [![Image 15: pyo3-utils-crates-v](https://camo.githubusercontent.com/0cff84a844cd0c3a25866033cc5d703abcbb22987457b7c9d275c89075791198/68747470733a2f2f696d672e736869656c64732e696f2f6372617465732f762f70796f332d7574696c73)](https://crates.io/crates/pyo3-utils) |  |
| codelldb | [![Image 16: codelldb-pypi-v](https://camo.githubusercontent.com/641b276ce3244b1d6bf36a6d7262b9bc93a854919a0cf2a54f983fb7971a8252/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f636f64656c6c6462)](https://pypi.org/project/codelldb) |  |  |

## Philosophy

[](https://github.com/pytauri/pytauri#philosophy)
### For Pythoneer

[](https://github.com/pytauri/pytauri#for-pythoneer)
I hope `PyTauri` can become an alternative to [pywebview](https://github.com/r0x0r/pywebview) and [Pystray](https://github.com/moses-palmer/pystray), leveraging Tauri's comprehensive features to offer Python developers a GUI framework and a batteries-included development experience similar to [electron](https://github.com/electron/electron) and [PySide](https://wiki.qt.io/Qt_for_Python).

> PyTauri is inspired by [FastAPI](https://github.com/fastapi/fastapi) and [Pydantic](https://github.com/pydantic/pydantic), aiming to offer a similar development experience.

### For Rustacean

[](https://github.com/pytauri/pytauri#for-rustacean)
Through [Pyo3](https://github.com/PyO3/pyo3), I hope Rust developers can better utilize the Python ecosystem (e.g., building AI GUI applications with [PyTorch](https://github.com/pytorch/pytorch)).

Although Rust's lifetime and ownership system makes Rust code safer, Python's garbage collection (GC) will make life easier. 😆

## Used By

[](https://github.com/pytauri/pytauri#used-by)
Although PyTauri is a fairly young project, a few people have used it to make cool projects:

*   [Digger Solo](https://solo.digger.lol/) - AI powered file manager

## Credits

[](https://github.com/pytauri/pytauri#credits)
PyTauri is a project that aims to provide Python bindings for [Tauri](https://github.com/tauri-apps/tauri), a cross-platform webview GUI library. `Tauri` is a trademark of the Tauri Program within the Commons Conservancy and PyTauri is not officially endorsed or supported by them. PyTauri is an independent and community-driven effort that respects the original goals and values of Tauri. PyTauri does not claim any ownership or affiliation with the Tauri Program.

## License

[](https://github.com/pytauri/pytauri#license)
This project is licensed under the terms of the _Apache License 2.0_.

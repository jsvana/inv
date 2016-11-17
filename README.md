# inv

`inv` is a keyboard inventory manager.

## Usage

List keyboards:

  python -m inv list

Add a keyboard:

  python -m inv add <form_factor> <make> <model> <serial>

Show a specific keyboard:

  python -m inv show <serial>

## Motivation

> Why on earth would you need a system to manage keyboard inventory?
> - Every Sane Person

Some people collect stamps; other people collect coins. I collect keyboards. Once you get over ~3 keyboards (I'm a bit past that) you need something to track all of them.

> Why not use Excel like a normal person?
> - Same group as before

First, I think we've established that I'm not a normal person. Second, I like to program and Excel is boring. Third, why not? "It seemed like a good idea at the time."

## Installation

`inv` requires Python 3.

Install requirements with:

  pip install -r requirements.txt

## License

[MIT](LICENSE)

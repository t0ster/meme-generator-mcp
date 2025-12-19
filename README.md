# Meme Generator MCP

An MCP (Model Context Protocol) server that generates memes with custom text overlays. Built with [FastMCP](https://github.com/jlowin/fastmcp) and [Pillow](https://pillow.readthedocs.io/).

https://github.com/user-attachments/assets/9b8b47f3-ec54-41ed-913c-a2807cbc93d4

## Features

- Generate memes from pre-configured templates
- Customizable text overlays with automatic word wrapping
- Extensible configuration for adding custom templates

## Available Memes

See [meme_configs.json](app/meme_configs.json) for the list of available memes and their text placeholders, and [meme_templates/](app/meme_templates/) for the template images.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## MCP Configuration

Add the server to your MCP client configuration:

```json
{
  "mcpServers": {
    "meme-generator": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/t0ster/meme-generator-mcp",
        "meme-generator-mcp"
      ]
    }
  }
}
```

## Local Development

```bash
git clone https://github.com/t0ster/meme-generator-mcp.git
cd meme-generator-mcp
uv sync
```

MCP configuration for local development:

```json
{
  "mcpServers": {
    "meme-generator": {
      "command": "uv",
      "args": ["run", "meme-generator-mcp", "--dev"]
    }
  }
}
```

The `--dev` flag uses local `app/meme_templates/` and `app/meme_configs.json` instead of copying to the config directory.

## Tools

### `get_meme_info`

Get information about available memes and their placeholder requirements.

**Parameters:**

- `meme_name` (optional): Get info for a specific meme

**Example:**

```json
{
  "meme_name": "drake_pointing"
}
```

### `generate_meme`

Generate a meme with custom text overlays.

**Parameters:**

- `meme_name`: The type of meme to generate
- `texts`: Dictionary mapping placeholder names to text values

**Example:**

```json
{
  "meme_name": "drake_pointing",
  "texts": {
    "disapprove": "Writing documentation",
    "approve": "Generating memes"
  }
}
```

Generated memes are saved to `~/.config/meme-generator-mcp/generated_memes/` by default (customizable via `MEME_GENERATOR_MCP_OUTPUT_PATH`).

## Environment Variables

| Variable                            | Description                             | Default                                          |
| ----------------------------------- | --------------------------------------- | ------------------------------------------------ |
| `MEME_GENERATOR_MCP_TEMPLATES_PATH` | Custom path to meme templates directory | `~/.config/meme-generator-mcp/meme_templates`    |
| `MEME_GENERATOR_MCP_OUTPUT_PATH`    | Custom path for generated memes         | `~/.config/meme-generator-mcp/generated_memes`   |
| `MEME_GENERATOR_MCP_CONFIGS_PATH`   | Custom path to meme configs JSON        | `~/.config/meme-generator-mcp/meme_configs.json` |

On Windows, the default config directory is `%LOCALAPPDATA%\meme-generator-mcp`.

## Adding Custom Memes

**For personal use:** Edit files in your config directory:

- `~/.config/meme-generator-mcp/meme_templates/` - add template images
- `~/.config/meme-generator-mcp/meme_configs.json` - add meme configurations

**For contributing (dev mode):** Edit files in the repo:

- `app/meme_templates/` - add template images
- `app/meme_configs.json` - add meme configurations

Configuration example:

```json
{
  "my_custom_meme": {
    "template_file": "my_template.jpg",
    "placeholders": {
      "top_text": {
        "x": 300,
        "y": 20,
        "max_width": 500,
        "align": "center",
        "font_size": 40,
        "fill": "white",
        "stroke_fill": "black",
        "stroke_width": 2
      }
    }
  }
}
```

### Placeholder Options

| Option         | Type   | Default    | Description                                        |
| -------------- | ------ | ---------- | -------------------------------------------------- |
| `x`            | int    | required   | X coordinate for text position                     |
| `y`            | int    | required   | Y coordinate for text position                     |
| `max_width`    | int    | required   | Maximum width before text wraps                    |
| `align`        | string | `"center"` | Text alignment: `"left"`, `"center"`, or `"right"` |
| `font_size`    | int    | `40`       | Font size in pixels                                |
| `fill`         | string | `"white"`  | Text color                                         |
| `stroke_fill`  | string | `"black"`  | Outline color                                      |
| `stroke_width` | int    | `2`        | Outline width in pixels                            |

## License

MIT

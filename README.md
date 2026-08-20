# DATASCI 350 final project starter

This is the starter repository for the DATASCI 350 final project. It gives
you a working pipeline on day one: a script that pulls data from the World
Bank API, a Quarto report that turns that data into a figure, and a
Dockerfile that renders the report inside a container.

Everything here is an example. Replace it with your own work. Keep the
structure.

## What is in the repository

| Path | What it does |
|------|--------------|
| `scripts/pull_data.py` | Calls the World Bank API once and saves the response to `data/raw/` |
| `data/raw/` | The saved data snapshot. Committed to the repository on purpose |
| `report.qmd` | The Quarto report, with headings that match the grading rubric |
| `requirements.txt` | The Python packages, pinned to exact versions |
| `Dockerfile` | The recipe that builds the container |

## The design rule

Read this part twice, because the rubric turns on it.

The pull script talks to the API. The report does not. The report reads
only the saved copy in `data/raw/`, and that snapshot is committed to the
repository.

The reason is simple. The API may change its format, rename an indicator,
or be down on the day I mark your project. If your report called the API
while rendering, it would break, and a report that does not render scores
nothing for reproducibility. With the snapshot committed, the container
renders the same report in December that it rendered in November, on any
machine, even with no internet connection.

So you pull once, commit the snapshot, and leave it alone.

## Getting started

Fork or clone this repository first. Work in your group's own copy.

### Step 1: pull the data

Open `scripts/pull_data.py`. Change the indicator, the countries, and the
years in the CONFIGURATION block near the top.

Run the script from the top folder of the repository.

```bash
python scripts/pull_data.py
```

The script writes two files into `data/raw/`. One is the raw JSON
response. The other is a tidy CSV.

Commit both files.

```bash
git add data/raw/
git commit -m "data: add World Bank snapshot"
```

### Step 2: build the container

Warning: the first build downloads Ubuntu, Quarto, and every Python
package. It takes several minutes. Later builds are much faster.

Run this command from the top folder of the repository.

```bash
docker build -t datasci350-project .
```

The `-t` flag names the image. The `.` tells Docker to use the current
folder as the build context.

### Step 3: render the report

Run the container.

```bash
docker run --rm -v "$(pwd)/output:/project/output" datasci350-project
```

The rendered report appears at `output/report.html`. Open it in a browser.

Here is what the flags mean.

- `--rm` deletes the container after it exits. The image stays.
- `-v "$(pwd)/output:/project/output"` connects the `output` folder inside
  the container to an `output` folder on your computer. Without it, the
  report renders inside the container and disappears with it.

## Test the container early

Warning: a Dockerfile that fails on the night of the deadline cannot be
fixed in time. Build the container in the first week of the project.

Test it the way I will test it. Do not test only in the folder where you
wrote the code, because that computer already has your packages installed.

1. Clone your repository into a new, empty folder.
2. Change into that folder.
3. Build the image.
4. Run the container.
5. Confirm that `output/report.html` exists and contains your figures.

If step 5 fails, your project fails the reproducibility criterion, which
is 30% of the grade.

## Adding a package

Add the package to `requirements.txt`. Pin it to an exact version with
`==`. Rebuild the image.

Do not install packages by hand inside a running container. Those changes
disappear, and my build will not have them.

## Reminders

Your report needs a research question, at least two visualisations,
analysis that fits the question, an honest limitations section, a note on
your use of AI, and a contribution statement.

Every group member must commit their own work to the repository. I read
the commit history.

Full instructions and the grading rubric are in the course repository,
under `project/project-instructions.pdf`.

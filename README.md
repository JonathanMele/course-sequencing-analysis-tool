# GSP Toolkit for Course Sequencing

The **GSP Toolkit** is a Python package that implements the Generalized Sequential Pattern (GSP) algorithm, with an initial focus on sequencing student course data. The toolkit supports both a command-line interface (CLI) and a graphical user interface (GUI), making it easy to use for a wide range of users.

Currently, the primary feature of the toolkit is to sequence and analyze course data using the GSP algorithm.

## Features

- **GSP Algorithm Implementation**: Discover sequential patterns in course data using the GSP algorithm.
- **Command-Line Interface (CLI)**: Use the GSP toolkit from the terminal for scripting or automation.
- **Graphical User Interface (GUI)**: An easy-to-use GUI for non-technical users to explore course sequencing results.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Fordham-EDM-Lab/course-sequencing-analysis-tool.git
   ```

2. Navigate to the project directory:
   ```bash
   cd course-sequencing-analysis-tool
   ```

3. Install the required dependencies:
   ```bash
   pip install .
   ```

## Usage

### Command-Line Interface (CLI)

The CLI allows you to run the GSP algorithm on course sequencing data. Here’s an example of how to use it:

```bash
gsp-cli --input-file courses.csv --output-dir results --min-support 0.5
```

- `--input-file`: The path to the CSV file containing course data.
- `--output-dir`: Directory where the results will be saved.
- `--min-support`: The minimum support threshold for the GSP algorithm.

### Graphical User Interface (GUI)

To launch the GUI for an easy-to-use interface:

```bash
gsp-gui
```

## Requirements

- Python 3.10 or later
- Required dependencies are automatically installed when you run `pip install .`.

## Example

Here’s a simple example of the input course data format (CSV):

```csv
SID,CourseCode,TermOrder,Semester,Year
1,CHEM101,20100,Spring,2010
1,CHEM102,20101,Summer,2010
1,PHYS101,20102,Fall,2010
2,MATH101,20100,Spring,2010
2,MATH102,20101,Summer,2010
```

Here:
- `SID` is the student ID.
- `CourseCode` is the course identifier.
- `TermOrder` combines `Year` and `Semester` for ordering courses.

## Development Roadmap

This package is currently focused on course sequencing, but future versions will include:
- A generalized GSP algorithm for other use cases.
- Additional CLI and GUI options.
- Improved concurrency support for larger datasets.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
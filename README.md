# tracky-mcpackage

Python CLI-initiated package tracking and driver management system

## Description

This is a Python app to provide for package tracking and driver support within a local delivery network.

## Getting Started

### Dependencies

- [sqlalchemy](https://www.sqlalchemy.org/)
- [alembic](https://github.com/sqlalchemy/alembic)
- [faker](https://faker.readthedocs.io/en/master/)
- [pytest](https://pytest.org)
- [textual](https://textual.textualize.io/)
- [mlrose](https://mlrose.readthedocs.io/en/stable/)

### Module documentation

- Home
- Driver Select that loads table of driver's current packages
- Packages
- View All or sort by status (tabbed windows)
- Real-time search
- Clicking on package opens an edit window to make changes to package, refreshes database and table on submit
- Add new package functionality that persists to database
- Customer
- View and search all customers
- Clicking on customer opens edit functionality that persists
- can add new customer
- Destination
  - View and search all destinations
  - Clicking on destination opens edit functionality that persists
  - can add new destination
- Best Path _beta_
  - Uses mlrose TravellingSalesperson algorithms to generate best delivery order for driver

### Modifying the source requires the above dependencies

### Executing program

## Authors

- Ethan Beneroff
- Michael Loomis
- Ty Blackwell
- Ainsley Alceme

## Version History

- 0.1
  - Initial Release

## License

This project is not licensed for any legitimate usage other than your own learning and amusement.

## Acknowledgments

Inspiration, code snippets, etc.

- [awesome-readme](https://github.com/matiassingers/awesome-readme)

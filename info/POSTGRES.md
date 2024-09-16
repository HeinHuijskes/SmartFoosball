## Postgres
For this project we used PostgreSQL as a database manager. This is because it is an easy to understand and intuitive manager which we have worked with before. This guide is made mostly for windows, though setting up the environment for other OSes should very much be possible.

### Installation
[Download the PostgreSQL installer](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) and follow the instructions. By default the name for a superuser is `postgres`, and the installer should ask you to set a password for it during setup. NOTE: make sure to include and enable Stack Builder while installing, and at the end of the install process open Stack Builder afterwards. This can help you while [installing some of the necessary extensions](#extensions).

### Create DB with shell
Creating a DB in a shell is mainly needed for the initial setup, so after that you can just use the PostgreSQL built in GUI instead. See [Create DB with pgAdmin](#create-db-with-pg-admin).

### Path
Add postgres to the PATH to be able to easily run the `psql` command from the command line. See also [this guide](https://www.commandprompt.com/education/how-to-set-windows-path-for-postgres-tools/).
- Type `env` in the windows searchbar and click `Edit the system environment variables`
- In the pop-up, click `Environment Variables`
- In the panel for your user, click `Path` and then the `Edit` button below
- Click `New`
- Enter the path to PostgreSQL bin (likely `C:\Program Files\PostgreSQL\16\bin`)

### Running
Postgres needs to be running to connect to it. This should happen automatically upon startup, though after install you may need to trigger it manually. To run postgres in terminal and create a database:
- Open a command prompt (`windows key` + `R`, enter `cmd`)
- Enter `psql -U postgres` (or replace `postgres` by your superuser)
- Enter your superuser password
- Enter `\l` to view existing databases
- Enter `CREATE DATABASE databasename;` to create a new one with name "databasename"
    - NOTE: Don't forget the `;`, otherwise the SQL won't work properly. Postgres notifies you for every succesful command, e.g. after the above it will respond with `CREATE DATABASE`
- Enter `\l` to see your new database listed
- Enter `\c databasename` to connect to the database
- (To delete a database: run `DROP DATABASE databasename;`. THIS WILL DELETE ALL DATA IN IT.)

### Create DB with pgAdmin
- Open the `pgAdmin 4` program (should be installed along with postgres)
- Create a server by rightclicking `Servers` and then `Register > Server`
    - Enter a name e.g. `project-server`
    - Go to the `Connection` tab, and enter `localhost` in the `Host name/address` field
    - Enter your superuser password in the password field
    - Click `Save`
- Expand your new server in the sidebar to see what it contains
- Rightclick your server, and select `Create > Database`
    - Enter a name in the `Database` section, e.g. `project-database`
    - Click `Save`

### Shell in pgAdmin (optional)
Now that you have setup pgAdmin, you can run a shell within the program much easier. To set this up:
- Click on `File > Preferences` in the top left
- Select `Paths > Binary paths`
- Select the correct version (e.g. `PostgreSQL 16`), and in the `Binary Path` field enter the postgres bin directory (e.g. `C:\Program Files\PostgreSQL\16\bin`)
- Click `Save`

To run the shell:
- Click on your database in the tab menu on the left
- Click on the `PSQL Tool` above the tab menu (its symbol looks like this: `">_"` )
- It should now automatically run a shell and log you into your database!

### Enter Schemas

#### Create tables
- Rightclick on your database and click `CREATE Script`
- Click on the `Open File` icon in the query menu, and open the `database.sql` file of this project (or any of the other files)
- Run the file, and all the tables should be installed
- To see this in the database tree menu on the left, go to `Project database > Schemas > public > Tables`, rightclick `Tables`, and select `Refresh`. It should now show the tables.
from cassandra.cluster import Cluster
from cassandra.protocol import ConfigurationException
import Geohash


class CassandraLogic:
    """Cassandra Logic class for manipulating, querying and inserting data.

       Args:
           contact_point (str): A contact point addresses a Cassandra cluster.
           keyspace (str): Name of the key space.
           create_keyspace (boolean): Whether to create a new key space or to just connect the session.

       Attributes:
           keyspace (str): Name of the key space.
           string_set (set): Columns names that are string type (the rest will be int by default).
           session (Session object): A session holds connections to a Cassandra cluster, allowing it to be queried.
       """

    def __init__(self, contact_point, keyspace, create_keyspace=True):
        self.contact_point = contact_point
        self.keyspace = keyspace
        self.string_set = set()
        self.string_set.add("pais")
        self.string_set.add("codigo_postal")
        self.string_set.add("pais_destino")
        self.string_set.add("competidor")
        self.string_set.add("divisa")
        self.string_set.add("modo_entrega")
        self.string_set.add("canal_captacion")
        self.string_set.add("user")
        self.string_set.add("ciudad")
        self.string_set.add("geohash")

        # Connect the application to the Cassandra cluster
        cluster = Cluster([contact_point], port=9042, cql_version='3.4.4')
        self.session = cluster.connect() if create_keyspace else cluster.connect(self.keyspace)

    @classmethod
    def from_existing_keyspace(cls, contact_point, keyspace):
        """Connect the Cassandra cluster to a certain key space.

           Returns:
               New Cassandra Logic instance.
        """
        return cls(contact_point, keyspace, False)

    def drop_and_create_keyspace(self):
        """Drop and create new key space.

            First, it tries to drop the key space and then it creates the key space.
            If the drop fails, it creates directly the key space.

            Returns:
                New Cassandra Logic instance
        """
        try:
            self.session.execute("Drop KEYSPACE {}".format(self.keyspace))
            self._create_keyspace()
        except ConfigurationException:
            self._create_keyspace()

        return self.connect_keyspace()

    def _create_keyspace(self):
        """Create new key space.

            Default parameters:
                replication strategy: SimpleStrategy
                replication factor: 3
        """
        create_keyspace_query = "CREATE KEYSPACE " + self.keyspace + " WITH replication = " \
                                                                     "{'class': 'SimpleStrategy', " \
                                                                     "'replication_factor' : 3}"
        self.session.execute(create_keyspace_query)

    def drop_and_create_tables(self, table_names):
        """Drop and create a table.

           First, it tries to drop the table and then it creates the table.
           If the drop fails, it creates directly the table.

           Args:
               table_name (str): name of the table.
        """
        for table_name in table_names:
            try:
                self.session.execute("DROP TABLE {}".format(table_name))
                self._create_table(table_name)

            except:
                self._create_table(table_name)

    def _create_table(self, table_name):
        """Create a table with a certain format.

            Args:
                table_name (str): name of the table.
        """
        if table_name == "query1":
            self._table1_scheme()
        elif table_name == "query2":
            self._table2_scheme()
        elif table_name == "query3":
            self._table3_scheme()
        elif table_name == "query4":
            self._table4_scheme()

    def insert_into_all_tables(self, data):
        if data['ciudad']:
            self._query1_scheme(data)
            self._query2_scheme(data)
        if data['lon'] and data['lat']:
            self._query3_scheme(data)
            self._query4_scheme(data)

    def _table1_scheme(self):
        table_name = "query1"
        create_table_query = "CREATE TABLE " + table_name + "(" \
                             + "pais_destino text, " \
                             + "ciudad text, " \
                             + "divisa text, " \
                             + "importe_destino double, " \
                             + "competidor text, " \
                             + "comision double, " \
                             + "tasa_cambio double, " \
                             + "timestamp double, " \
                             + "PRIMARY KEY (pais_destino, ciudad, divisa, importe_destino, competidor))" \
                               "WITH CLUSTERING ORDER BY (ciudad DESC, divisa DESC, importe_destino DESC, competidor DESC);"

        self.session.execute(create_table_query)

    def _query1_scheme(self, data):
        table_name = "query1"
        column_names = ["ciudad", "pais_destino", "divisa", "competidor", "comision", "tasa_cambio", "timestamp"]
        column_values = []
        for i in column_names:
            column_values.append(data[i])

        column_names.append("importe_destino")
        importe_destino = 100*float(data["tasa_cambio"]) - float(data["comision"])
        column_values.append(importe_destino)
        self._insert_data(table_name, column_names, column_values)

    def _table2_scheme(self):
        table_name = "query2"
        create_table_query = "CREATE TABLE " + table_name + "(" \
                             + "pais_destino text, " \
                             + "ciudad text, " \
                             + "divisa text, " \
                             + "competidor text, " \
                             + "importe_destino double, " \
                             + "comision double, " \
                             + "tasa_cambio double, " \
                             + "timestamp double, " \
                             + "PRIMARY KEY (pais_destino, ciudad, divisa, competidor, importe_destino))" \
                               "WITH CLUSTERING ORDER BY (ciudad DESC, divisa DESC, competidor DESC, importe_destino DESC);"

        self.session.execute(create_table_query)

    def _query2_scheme(self, data):
        table_name = "query2"
        column_names = ["ciudad", "pais_destino", "divisa", "competidor", "comision", "tasa_cambio", "timestamp"]
        column_values = []
        for i in column_names:
            column_values.append(data[i])

        column_names.append("importe_destino")
        importe_destino = 100*float(data["tasa_cambio"]) - float(data["comision"])
        column_values.append(importe_destino)
        self._insert_data(table_name, column_names, column_values)

    def _query3_scheme(self, data):
        table_name = "query3"
        column_names = ["pais_destino", "divisa", "competidor", "comision", "tasa_cambio", "timestamp", "lat", "lon", "ciudad"]
        column_values = []
        for i in column_names:
            column_values.append(data[i])

        column_names.append("importe_destino")
        importe_destino = 100*float(data["tasa_cambio"]) - float(data["comision"])
        column_values.append(importe_destino)

        column_names.append("geohash")
        column_values.append(Geohash.encode(float(data['lat']), float(data['lon'])))
        self._insert_data(table_name, column_names, column_values)

    def _table3_scheme(self):
        table_name = "query3"
        create_table_query = "CREATE TABLE " + table_name + "(" \
                             + "pais_destino text, " \
                             + "divisa text, " \
                             + "geohash text, " \
                             + "importe_destino double, " \
                             + "competidor text, " \
                             + "comision double, " \
                             + "tasa_cambio double, " \
                             + "timestamp double, " \
                             + "lat double, " \
                             + "lon double, " \
                             + "ciudad text, " \
                             + "PRIMARY KEY (pais_destino, divisa, geohash, importe_destino, competidor))" \
                               "WITH CLUSTERING ORDER BY (divisa DESC, geohash DESC, importe_destino DESC, competidor DESC);"

        self.session.execute(create_table_query)

    def _query4_scheme(self, data):
        table_name = "query4"
        column_names = ["pais_destino", "divisa", "competidor", "comision", "tasa_cambio", "timestamp", "lat", "lon", "ciudad"]
        column_values = []
        for i in column_names:
            column_values.append(data[i])

        column_names.append("importe_destino")
        importe_destino = 100 * float(data["tasa_cambio"]) - float(data["comision"])
        column_values.append(importe_destino)

        column_names.append("geohash")
        column_values.append(Geohash.encode(float(data['lat']), float(data['lon'])))
        self._insert_data(table_name, column_names, column_values)

    def _table4_scheme(self):
        table_name = "query4"
        create_table_query = "CREATE TABLE " + table_name + "(" \
                             + "pais_destino text, " \
                             + "divisa text, " \
                             + "competidor text, " \
                             + "geohash text, " \
                             + "importe_destino double, " \
                             + "comision double, " \
                             + "tasa_cambio double, " \
                             + "timestamp double, " \
                             + "lat double, " \
                             + "lon double, " \
                             + "ciudad text, " \
                             + "PRIMARY KEY (pais_destino, divisa, competidor, geohash, importe_destino))" \
                               "WITH CLUSTERING ORDER BY (divisa DESC, competidor DESC, geohash DESC, importe_destino DESC);"

        self.session.execute(create_table_query)

    def _insert_data(self, table_name, column_names, column_values):
        """Insert a row in a table

           Notice we do not need to include all the columns names nor columns values due to the flexible schema.
           The column values are integer by default, except if they are included in the string_set.

           Args:
               table_name (str): name of the table.
               column_names (list): name of the columns to insert.
               column_values (list): values of the columns to insert.
        """
        insert_data_query = "INSERT INTO {} (".format(table_name)
        insert_data_query += ",".join(column_names)
        insert_data_query += ") VALUES("
        processed_values = ["'"+c+"'" if column_names[cont] in self.string_set else str(c) for cont, c in enumerate(column_values)]
        insert_data_query += ",".join(processed_values)
        insert_data_query += ");"

        self.session.execute(insert_data_query)

    def select_all(self, table_name):
        """Select all the information of a table

           Args:
               table_name (str): name of the table.

            Returns:
                All the rows of the table.
        """
        results = self.session.execute("SELECT * FROM {}".format(table_name))
        rows = []
        for res in results:
            row = []
            for r in res:
                row.append(str(r))
            rows.append(row)
        return rows

    def best_tasa_given_ciudad(self, table_name, ciudad, pais_destino, divisa, competidor=None):
        query = "SELECT * FROM {} ".format(table_name)
        query += "WHERE pais_destino='{}' AND ciudad='{}' AND divisa='{}' ".format(pais_destino, ciudad, divisa)
        if competidor:
            query += "AND competidor='{}' ".format(competidor)
        query +=  "LIMIT 1"
        results = self.session.execute(query)
        rows = []
        for res in results:
            row = []
            for r in res:
                row.append(str(r))
            rows.append(row)
        return rows

    def best_tasa_given_coordinates(self, table_name, pais_destino, divisa, geohash_max, geohash_min, mostrar, competidor=None):
        query = "SELECT * FROM {} ".format(table_name)
        query += "WHERE pais_destino='{}' AND divisa='{}' ".format(pais_destino, divisa)
        if competidor:
            query += "AND competidor='{}' ".format(competidor)
        query += "AND geohash < '{}' AND geohash > '{}' ".format(geohash_max, geohash_min)
        query += "LIMIT {}".format(mostrar)
        results = self.session.execute(query)

        rows = []
        for res in results:
            row = []
            for r in res:
                row.append(str(r))
            rows.append(row)
        return rows

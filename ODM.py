__author__ = 'Pablo Ramos Criado'
__students__ = 'Noémie Guillaume' 'Alberto Fernández'



from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from typing import Generator, Any, Self
from geojson import Point
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import yaml

def getLocationPoint(address: str) -> Point:
    """ 
    Obtain the coordinates of an address in geojson.Point format.
    Use the geopy API to retrieve the address coordinates.
    Note: The API is public and has request limits; use sleep intervals.

    Parameters
    ----------
        address : str
            Full address for which to obtain coordinates.
    Returns
    -------
        geojson.Point
            Coordinates of the address point.
    """
    location = None
    attempts = 0
    maxAttempts = 5

    while location is None and attempts < maxAttempts:
        attempts += 1
        try:
            time.sleep(1)
            # Changed: the skeleton had a placeholder user_agent; Nominatim
            # just needs some identifying string, not a real name.
            location = Nominatim(user_agent="envivo-utad-abd-app").geocode(address)
        except GeocoderTimedOut:
            # May raise if the request times out. We just retry on the
            # next pass of the while loop.
            continue

    if location is None:
        # Do not invent a point and do not return None: Phase 2 needs to
        # be able to tell "could not be geolocated" apart from a valid
        # point.

        raise ValueError(
            f"No se pudieron obtener coordenadas: {address!r}"
        )

    # GeoJSON represents points as (longitude, latitude), the reverse of
    # geopy's location.latitude / location.longitude.
    return Point((location.longitude, location.latitude))

class Model:
    """ 
    Abstract model class
    Create as many subclasses of this class as there are  
    collections/models desired in the database.

    Attributes
    ----------
        required_vars : set[str]
            set of attributes required by the model
        admissible_vars : set[str]
            set of attributes accepted by the model
        db : pymongo.collection.Collection
            connection to the database collection
    
    Methods
    -------
        __setattr__(name: str, value: str | dict) -> None
            Overrides the method for assigning values ​​to object attributes
            to control which attributes are modified and when.
        __getattr__(name: str) -> Any
            Overrides the method for accessing object attributes.
        save() -> None
            Saves the model to the database.
        delete() -> None
            Deletes the model from the database.
        find(filter: dict[str, str | dict]) -> ModelCursor
            Performs a read query on the database.
            Returns a ModelCursor.
        aggregate(pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor
            Returns the result of an aggregate query.
        find_by_id(id: str) -> dict | None
            Searches for a document by its ID using the cache and returns it.
            Returns None if the document is not found.
        init_class(db_collection: pymongo.collection.Collection, required_vars: set[str], admissible_vars: set[str]) -> None
            Initializes class variables during system initialization.
    """
    _required_vars: set[str]
    _admissible_vars: set[str]
    _location_var: str | None = None
    _db: pymongo.collection.Collection
    _internal_vars: set[str] = frozenset(('_modified_vars', '_required_vars', '_admissible_vars', '_db', '_data', '_location_var'))

    def __init__(self, **kwargs: dict[str, str | dict | list]) -> None:
        """
        Initializes the model with the values ​​provided in kwargs.
        Verifies that the values ​​provided in kwargs are supported
        by the model and that the required attributes are provided.

        Parameters
        ----------
            kwargs : dict[str, str | dict]
                Dictionary containing the model attribute values.
        """
        #TODO
        # Perform necessary checks and operations
        # before assignment.
        # Assign all values ​​in kwargs to attributes named 
        # after the keys in kwargs.
        # We use the 'data' attribute to store database-stored 
        # variables within a single attribute.
        # Encapsulating the data in a single variable simplifies 
        # management in methods such as 'save'.
        keys = set(kwargs.keys())
        for key in keys :
            if key not in self._admissible_vars:
                raise ValueError(f"Value {key} not in admissibles values")
        
        for require in self._required_vars:
            if require not in keys:
                raise ValueError(f"Required values {require} is missing")
        
        self._data: dict[str, str | dict | list] = {}
        
        self._data.update(kwargs)

    def __setattr__(self, name: str, value: str | dict) -> None:
        """ Overrides the method for assigning values ​​to the object's 
        attributes in order to control which attributes are modified 
        and when.
        """
        # If name is an Model parameters
        if name in self._internal_vars:
            super().__setattr__(name, value)
            return
        #TODO
        # Carry out the necessary checks and arrangements
        # before the assignment.
        if name not in self._admissible_vars:
                raise ValueError(f"Value {name} not in admissibles values")
        
        #Save the modification in _modified_vars
        self._modified_vars(name)

        # Assign the value `value` to the variable `name`
        self._data[name] = value

    def __getattr__(self, name: str) -> Any:
        """ Overrides the object's attribute access method;
        __getattr__ is only called when the attribute is not found
        on the object.
        """
        if name in self._internal_vars:
            return super().__getattribute__(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError
        
    def save(self) -> None:
        """
        Saves the model to the database.
        If the model does not exist in the database, a new
        document is created with the model's values. Otherwise, the
        existing document is updated with the new model
        values.
        """
        #TODO
        #ADD check if needs the location !!!
        #This document has already a _data ?
        if "_id" in self._data :
            self._db.update_one(
                {"_id": self._data["_id"]},
                {"$set": self._data}
                )
        #If new  == no _data
        else:
            result_insert = self._db.insert_one(self._data)
            
            #Save the id created by the insertion
            self._data["_id"] = result_insert.inserted_id



        #pass #Don't forget to remove this line once implemented

    def delete(self) -> None:
        """
        Deletes the model from the database.
        """
        if '_id' in self._data:
            self._db.delete_one({'_id': self._data['_id']})
            del self._data['_id']
    
    @classmethod
    def find(cls, filter: dict[str, str | dict]) -> Any:
        """ 
        Utiliza el metodo find de pymongo para realizar una consulta
        de lectura en la BBDD.
        find debe devolver un cursor de modelos ModelCursor

        Parameters
        ----------
            filter : dict[str, str | dict]
                diccionario con el criterio de busqueda de la consulta
        Returns
        -------
            ModelCursor
                cursor de modelos
        """ 
        #TODO
        # cls es el puntero a la clase
        pass #No olvidar eliminar esta linea una vez implementado

    @classmethod
    def aggregate(cls, pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor:
        """ 
        Devuelve el resultado de una consulta aggregate. 
        No hay nada que hacer en esta funcion.
        Se utilizara para las consultas solicitadas
        en el segundo proyecto de la practica.

        Parameters
        ----------
            pipeline : list[dict]
                lista de etapas de la consulta aggregate 
        Returns
        -------
            pymongo.command_cursor.CommandCursor
                cursor de pymongo con el resultado de la consulta
        """ 
        return cls._db.aggregate(pipeline)
    
    @classmethod
    def find_by_id(cls, id: str) -> Self | None:
        """ 
        NO IMPLEMENTAR HASTA EL TERCER PROYECTO
        Busca un documento por su id utilizando la cache y lo devuelve.
        Si no se encuentra el documento, devuelve None.

        Parameters
        ----------
            id : str
                id del documento a buscar
        Returns
        -------
            Self | None
                Modelo del documento encontrado o None si no se encuentra
        """ 
        #TODO
        pass

    @classmethod
    def init_class(cls, db_collection: pymongo.collection.Collection, indexes:dict[str,str], required_vars: set[str], admissible_vars: set[str], location_var : None) -> None:
        """ 
        Initializes class attributes during system initialization.
        Indexes should be initialized or verified here. Any other
        initialization, checks, or additional changes deemed
        appropriate by the student may also be performed.

        Parameters
        ----------
            db_collection : pymongo.collection.Collection
                Connection to the database collection.
            indexes: Dict[str,str]
                Set of indexes and index types for the collection.
            required_vars : set[str]
                Set of attributes required by the model.
            admissible_vars : set[str] 
                Set of attributes accepted by the model.
        """
        cls._db = db_collection
        cls._required_vars = required_vars
        cls._admissible_vars = admissible_vars
        # TODO
        # Iterate through indexes and create each one based on its type: 'unique', 'asc',
        # or 'geosphere'. Compare the type for equality, not using the 'in' operator.
        # Pay attention to the geospatial index: save() stores the GeoJSON Point in
        # <field>_loc, so the 2dsphere index is applied to <field>_loc, whereas
        # _location_var must store the name of the base field.


class ModelCursor:
    """ 
    Cursor para iterar sobre los documentos del resultado de una
    consulta. Los documentos deben ser devueltos en forma de objetos
    modelo.

    Attributes
    ----------
        model_class : Model
            Clase para crear los modelos de los documentos que se iteran.
        cursor : pymongo.cursor.Cursor
            Cursor de pymongo a iterar

    Methods
    -------
        __iter__() -> Generator
            Devuelve un iterador que recorre los elementos del cursor
            y devuelve los documentos en forma de objetos modelo.
    """

    def __init__(self, model_class: Model, cursor: pymongo.cursor.Cursor):
        """
        Inicializa el cursor con la clase de modelo y el cursor de pymongo

        Parameters
        ----------
            model_class : Model
                Clase para crear los modelos de los documentos que se iteran.
            cursor: pymongo.cursor.Cursor
                Cursor de pymongo a iterar
        """
        self.model = model_class
        self.cursor = cursor
    
    def __iter__(self) -> Generator:
        """
        Devuelve un iterador que recorre los elementos del cursor
        y devuelve los documentos en forma de objetos modelo.
        Utilizar yield para generar el iterador
        Utilizar la funcion next para obtener el siguiente documento del cursor
        Utilizar alive para comprobar si existen mas documentos.
        """
        #TODO
        pass #No olvidar eliminar esta linea una vez implementado


def initApp(definitions_path: str = "./models_test.yml", mongodb_uri="mongodb://localhost:27017/", db_name="abd", scope=globals()) -> None:
    """ 
    Declare the classes that inherit from Model for each of
    the models belonging to the collections defined in 
    `definitions_path`. Initialize the model classes by 
    providing the supported and required indexes and attributes
    for each, as well as the connection to the database collection.
    
    Parameters
    ----------
        definitions_path : str
            path to the model definitions file
        mongodb_uri : str
            database connection URI
        db_name : str
            database name
    """
    #TODO
    # Initialise the database
    client = pymongo.MongoClient(mongodb_uri)
    db = client[db_name]

    #TODO
    # Declare as many model classes as there are collections in the database
    # Read the model definition file to obtain the collections,
    with open(definitions_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # indexes, and the allowed and required attributes for each of them.
    # Example of a model declaration for a collection named MiModelo
    #scope["MiModelo"] = type("MiModelo", (Model,),{})
    for model_name, model_info in config.items():
        name = model_name
        required_vars = model_info.get("required_vars", [])
        admissible_vars = model_info.get("admissible_vars", [])
        indexes = model_info.get("indexes", {})
        location_var = model_info.get("location_var", None)

        scope[name] = type(name, (Model,),{})

        # The class is declared at runtime and exists within a specific scope—which
        # need not be the global namespace, as the tests pass it their own
        # dictionary. That is why it is initialized via the scope rather than
        # by name, since the name does not yet exist at that point.
        #scope["MiModelo"].init_class(db_collection=None, indexes=None, required_vars=None, admissible_vars=None)
        scope[name].init_class(db_collection=db[name], indexes=indexes, required_vars=required_vars, admissible_vars=admissible_vars, location_var=location_var)

if __name__ == '__main__':
    
    # Inicializar base de datos y modelos con initApp
    #TODO
    initApp()

    #Ejemplo
    m = MiModelo(nombre="Pablo", apellido="Ramos", edad=18)
    m.save()
    m.nombre="Pedro"
    print(m.nombre)

    # Hacer pruebas para comprobar que funciona correctamente el modelo
    #TODO
    # Crear modelo

    # Asignar nuevo valor a variable admitida del objeto 

    # Asignar nuevo valor a variable no admitida del objeto 

    # Guardar

    # Asignar nuevo valor a variable admitida del objeto

    # Guardar

    # Buscar nuevo documento con find

    # Obtener primer documento

    # Modificar valor de variable admitida

    # Guardar

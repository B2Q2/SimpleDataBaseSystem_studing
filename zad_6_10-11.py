import os
from types import NoneType

def printif( *values, visual=True, sep=" ", end= '\n ',):
    if visual:
        print(*values, sep=sep, end=end)

class records():
    recordObjects: list['records'] = []
    visibleAction:bool = False

    def __init__(self, name=None, datatype=None, isKeyID:bool = False) -> None:
        self.name:str = name
        self.datatype:any = datatype

        if isKeyID:
            self.insert(0, self)
        else:
            self.new(self)
    
    @classmethod
    def addnew(self, name:str = None, datatype:any = None, isKeyID:bool = False)->'records':
        assert isinstance(name, str), " Err... Nieporawny typ Nazwy!"
        assert not isinstance(datatype, NoneType), " Err... Brak podanego Typu rekordu!"
        assert records.nameIsUnic(name), " Err... Nazwa nie jest unikatowa!"
        
        obj = self.__new__(self)
        obj.__init__(name, datatype, isKeyID)

        print(f" >> Utworzono rekord {name} typu {datatype}, klucz {isKeyID}")

        return obj

    @staticmethod
    def new(object:'records'):
        printif(" .. .. stworzenie nowego rekordu", visual=records.visibleAction)
        records.recordObjects.append(object)
    
    @staticmethod
    def insert(index, object:'records'):
        printif( f" .. .. wstawienie nowego rekordu na index:{index}", visual=records.visibleAction)
        records.recordObjects.insert(index, object)

    @staticmethod
    def get()->list['records']:
        printif(" .. .. pobrano listę rekordów", visual=records.visibleAction)
        return records.recordObjects

    @staticmethod
    def nameIsUnic(name:str):
        for rec in records.get():
            printif( f" .. .. .. znaleziono {rec.name}", visual=records.visibleAction)
            if name == rec:
                return False
        else:
            printif( f" .. .. .. brak dublikatów, nazw", visual=records.visibleAction)
            return True

    def __str__(self)->str:
        msg:str = f" .. Rekord {self.name}\ttypu\t{self.datatype}"
        return msg

    @staticmethod
    def get_str()->str:
        msg = " ## Wyswietlanie Stworzone Rekordy w  bazie danych:\n"
        for rec in records.get():
            msg = msg + str(rec) + '\n'
        return msg

    @staticmethod
    def get_name()->list[str]:
        atr: list = []
        for rec in records.get():
            atr.append( rec.name )
        return atr
    
    @staticmethod
    def get_datatype()->list[any]:
        atr: list = []
        for rec in records.get():
            atr.append( rec.datatype )
        return atr

    @staticmethod
    def get_length()->int:
        return records.get().__len__()

class datacell():
    def __init__(self, DB_records:records) -> None:
        assert DB_records == records, " Err... Brak podanych rekordów pola!"
        
        self.set_data_area( DB_records )

        print(" >> Stworzono nowy zbiór danych. ")
    
    def set_data_area(self, DB_records:records, update_data_val:NoneType|list[any] = None):
        self.records:records = DB_records

        index = 0

        for rec_name in self.records.get_name():
            if isinstance(update_data_val, NoneType):
                setattr(self, rec_name, None)
            else:
                setattr(self, rec_name, update_data_val[index])
                index += 1

    def add_data(self, *data_values):
        assert data_values.__len__() == self.records.get_length(), " Err... Nieodpowiednia ilość danych!"

        for rec_datatype, data_val in zip(self.records.get_datatype(), data_values):
            if rec_datatype != type(data_val):
                raise TypeError(" Err... Niepoprawny typ wprowadzanych danych! {}".format(data_val) )

        self.set_data_area(self.records, data_values)

        print(" >> Dodano dane do zbioru danych. ")
    
    def __str__(self) -> str:
        msg:str = " ## Wyswietlanie Informacje o polu.\n"
        fillter_record_name = self.records.get_name()
        
        for dc_val_name, dc_val in vars(self).items():
            if dc_val_name in fillter_record_name:
                msg = msg + f" .. {dc_val_name}: {dc_val}\n"

        return msg

class database():
    def __init__(self) -> None:

        self.records = records
        self.records.visibleAction = False
        self.ID = 0
        self.data: list[datacell] = list()
        self.record_ID_name = None
        # methods
    
    def add_record(self, name:str, datatype:any ):
        if name[0] == '*':
            if isinstance(self.record_ID_name, NoneType):
                assert not isinstance(datatype, int), " Err... Źle ustawiony typ danych dla klucza!"
                print(" >> Zdefinowano klucz {}".format( name ) )
                name = name[1:]
                self.record_ID_name = name
                self.records.addnew(name, datatype, True)
            else:
                raise ValueError(" Err... Zdefiniowano już pole kluczowe! ")
        else:
            self.records.addnew(name, datatype)

    def add_data(self, *data_valus):
        assert self.record_ID_name in self.records.get_name(), " Err... Niezdefiniowano pola ID klucza!"
        
        data_valus = [self.ID] + list(data_valus)
        self.ID += 1
        newData = datacell(self.records)
        newData.add_data(*data_valus)
        self.data.append( newData )
    
    def del_data(self, ID_key:int):
        assert ID_key in self.load_dataIsName(self.record_ID_name), " Err... Nieznaleziono wskazanego klucza:{}!".format(ID_key)

        deccress: bool = False
        for dc in self.data.copy():
            if getattr(dc, self.record_ID_name) == ID_key:
                self.data.remove( dc )
                self.ID -= 1
                deccress = True
            elif deccress: 
                val = getattr(dc, self.record_ID_name) - 1
                setattr(dc, self.record_ID_name, val)

    def load_dataIsName(self, name)->list:
        atr:list = []
        for d in self.data:
            if hasattr(d, name):
                val = getattr(d, name)
                atr.append( val )

        return atr

    def get_datacell(self, indexID:int)->datacell|None:
        for data_val in self.data:
            if hasattr(data_val, "ID"):
                if getattr(data_val, "ID") == indexID:
                    return data_val
        else:
            return None

    def __str__(self) -> str:
        msg = "\n ## Wyświetlono dane Bazy Danych:\n\n"

        for ID_key in self.load_dataIsName(self.record_ID_name):
            dc = self.get_datacell(ID_key)
            msg = msg + " .. " + str(dc) + '\n'
        return msg

if __name__ == "__main__":
    DB = database()

    DB.add_record("imie", str)
    DB.add_record("nazw", str)
    DB.add_record("*ID", int)
    DB.add_record("wiek", int)

    DB.add_data("Antoni", "Peroni", 10)
    DB.add_data("Filip", "Rondel", 12)
    DB.add_data("Ginter", "Kaling", 14)

    print(DB)
    DB.del_data(0)
    print(DB)



import re
import copy

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
FILE_TYPE_SLK = 1
FILE_TYPE_TXT = 2
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class slk_object:

    def __init__(self, obj_id, obj_dict, col_attr):
        self.__dict = {}
        self.__id = obj_id
        for key, value in col_attr.items():
            if value in obj_dict:
                self.__dict[key] = obj_dict[value]
            
    def __getitem__(self, tag):
        if tag == 'typeid' :
            return self.__id[1:-1]
        else:
            return self.__dict['"'+tag+'"']
        
    def __contains__(self, tag):
        if tag == 'typeid' :
            return True
        else:
            return '"'+tag+'"' in self.__dict

    def __add__(self, other):
        for key, value in other.items():
            self.__dict[key] = value
        
    def items(self):
        for key, value in self.__dict.items():
            yield key[1:-1], value

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class txt_object:

    def __init__(self, obj_id, obj_dict):
        self.__dict = obj_dict
        self.__id = obj_id
            
    def __getitem__(self, tag):
        if tag == 'typeid' :
            return self.__id
        else:
            return self.__dict[tag]
        
    def __contains__(self, tag):
        if tag == 'typeid' :
            return True
        else:
            return tag in self.__dict
        
    def __add__(self, other):
        for key, value in other.items():
            self.__dict[key] = value
        
    def items(self):
        for key, value in self.__dict.items():
            yield key, value

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
  
class txt_single:

    def __init__(self, path):
        self.__taglist = {}
        self.__dict = {}
        self.__load(path)
            
    def __getitem__(self, id):
        return txt_object(id, self.__dict[id])

    def has_tag(self, tag):
        if tag not in self.__taglist:
            return False
        return True

    def get(self, id, tag):
        try:
            return self.__dict[id][tag]
        except:
            return None

    def set(self, id, tag, value):
        try:
            self.__dict[id][tag] = value
        except:
            pass

    def save(self, path):
        self.__save(path)

    def new(self, id, copy_id):
        if copy_id not in self.__dict:
            return
        self.__dict[id] = copy.deepcopy(self.__dict[copy_id])
            
    def items(self):
        for key, value in self.__dict.items():
            yield txt_object(key, value)
            
#------------------------------------------------------------------------------
#private:
#------------------------------------------------------------------------------
    def __set_value(self, id, tag, value):
        if tag not in self.__taglist:
            self.__taglist[tag] = 0
        if id not in self.__dict:
            self.__dict[id] = {}
        self.__dict[id][tag] = value

    __id_re = re.compile(r"""
        \[(?P<ID>[A-Za-z0-9]{4})\]
        """, re.VERBOSE)
    __tag_re = re.compile(r"""
        (?P<TAG>[A-Za-z0-9]+)=(?P<VALUE>.*)
        """, re.VERBOSE)
    def __load(self, path):	
        try:
            fp = open(path, 'r')
            try:
                cur_id = ''
                line = fp.readline()
                # UTF-8 BOM
                if len(line)>=3 and line[0] == '\xEF' and line[1] == '\xBB' and line[2] == '\xBF':
                    line = line[3:]
                while line:
                    m = self.__id_re.match(line)
                    if m:
                        cur_id = m.group('ID')
                    else:
                        m = self.__tag_re.match(line)
                        if m:
                            self.__set_value(cur_id, m.group('TAG'), m.group('VALUE'))
                    line = fp.readline()
            finally:
                fp.close()
        except IOError:
            pass

    def __save(self, path):
        try:
            fp = open(path, 'w')
            try:
                for id in self.__dict.keys():
                    fp.write('[%s]\n' % id)
                    obj = self.__dict[id]
                    for tag in obj.keys():
                        fp.write('%s=%s\n' % (tag, obj[tag]))
            finally:
                fp.close()
        except IOError:
            pass

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class slk_single:

    def __init__(self, path):
        self.__row = {}
        self.__col = {}
        self.__dict = {}
        self.__cur_x = 0
        self.__cur_y = 0
        self.__max_x = 0
        self.__max_y = 0
        self.__load(path)
            
    def __getitem__(self, id):
        return slk_object(id, self.__dict[self.__row['"'+id+'"']], self.__col)

    def has_tag(self, tag):
        if '"'+tag+'"' not in self.__col:
            return False
        return True

    def get(self, id, tag):
        try:
            return self.__dict[self.__row['"'+id+'"']][self.__col['"'+tag+'"']]
        except:
            return None

    def set(self, id, tag, value):
        try:
            self.__dict[self.__row['"'+id+'"']][self.__col['"'+tag+'"']] \
                = value
        except:
            pass

    def save(self, path):
        self.__save(path)

    def new(self, id, copy_id):
        if '"'+copy_id+'"' not in self.__row:
            return
        y = self.__row['"'+copy_id+'"']
        self.__max_y += 1
        self.__dict[self.__max_y] = copy.deepcopy(self.__dict[y])
        self.__row['"'+id+'"'] = self.__max_y
        self.__dict[self.__max_y][1] = '"'+id+'"'
                
    def items(self):
        id_dict = {}
        for key, value in self.__row.items():
            id_dict[value] = key
        for key, value in self.__dict.items():
            if key in id_dict:
                yield slk_object(id_dict[key], value, self.__col)

#------------------------------------------------------------------------------
#private:
#------------------------------------------------------------------------------
    def __set_value(self, value):
        if self.__cur_y == 1:
            self.__col[value] = self.__cur_x
        elif self.__cur_x == 1:
            self.__row[value] = self.__cur_y
        if self.__cur_y not in self.__dict:
            self.__dict[self.__cur_y] = {}
        self.__dict[self.__cur_y][self.__cur_x] = value

    def __read_value(self, line):
        for elem in line.split(';'):
            if elem[0] == 'X':
                self.__cur_x = int(elem[1:])
            elif elem[0] == 'Y':
                self.__cur_y = int(elem[1:])
            elif elem[0] == 'K':
                self.__set_value(elem[1:])

    def __load(self, path):
        try:
            fp = open(path, 'r')
            try:
                line = fp.readline()
                if (line.strip() != 'ID;PWXL;N;E'):
                    return
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line == '':
                        continue
                    if line[0] == 'E':
                        break
                    elif line[0] == 'C':
                        if line[1] != ';':
                            continue
                        self.__read_value(line[2:])
                    elif line[0] == 'B':
                        if line[1] != ';':
                            continue
                        for elem in line[2:].split(';'):
                            if elem[0] == 'X':
                                self.__max_x = int(elem[1:])
                            elif elem[0] == 'Y':
                                self.__max_y = int(elem[1:])
            finally:
                fp.close()
        except IOError:
            pass

    def __save(self, path):
        try:
            fp = open(path, 'w')
            try:
                fp.write('ID;PWXL;N;E\n')
                fp.write('B;X%d;Y%d;D0\n' % (self.__max_x, self.__max_y))
                for y in range(1, self.__max_y+1):
                    for x in range(1, self.__max_x+1):
                        if y in self.__dict and x in self.__dict[y]:
                            if x != 1:
                                fp.write('C;X%d;K%s\n' % \
                                    (x, self.__dict[y][x]))
                            else:
                                fp.write('C;X%d;Y%d;K%s\n' % \
                                    (x, y, self.__dict[y][x]))
                fp.write('E\n')
            finally:
                fp.close()
        except IOError:
            pass

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class slk_multi():

    def __init__(self, in_dir, out_dir, file_list):
        self.__in_dir = in_dir
        self.__out_dir = out_dir
        self.__file = []
        self.__file_name = []
        for file_type, file_name in file_list:
            if file_type == FILE_TYPE_SLK:
                self.__file_name.append(file_name)
                self.__file.append(slk_single(self.__in_dir + '/' + file_name))
            elif file_type == FILE_TYPE_TXT:
                self.__file_name.append(file_name)
                self.__file.append(txt_single(self.__in_dir + '/' + file_name))
    
    def get(self, id, tag):
        for f in self.__file:
            ret = f.get(id, tag)
            if ret is not None:
                return ret
        return None
    
    def set(self, id, tag, value):
        for f in self.__file:
            if f.has_tag(tag):
                f.set(id, tag, value)
                
    def save(self):
        for f in self.__file:     
            f.save(self.__out_dir + '/' + self.__file_name[self.__file.index(f)])

    def new(self, id, copy_id):
        for f in self.__file:
            f.new(id, copy_id)        

    def items(self):
        for f in self.__file:
            for obj in f.items():
                yield obj

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class slk_unit(slk_multi):
    
    def __init__(self, in_dir, out_dir):
        file_list = [(FILE_TYPE_SLK, 'unitbalance.slk'), \
                     (FILE_TYPE_SLK, 'unitdata.slk'), \
                     (FILE_TYPE_SLK, 'unitui.slk'), \
                     (FILE_TYPE_SLK, 'unitweapons.slk'), \
                     (FILE_TYPE_TXT, 'campaignunitfunc.txt'), \
                     (FILE_TYPE_TXT, 'campaignunitstrings.txt'), \
                     (FILE_TYPE_TXT, 'humanunitfunc.txt'), \
                     (FILE_TYPE_TXT, 'humanunitstrings.txt'), \
                     (FILE_TYPE_TXT, 'nightelfunitfunc.txt'), \
                     (FILE_TYPE_TXT, 'nightelfunitstrings.txt'), \
                     (FILE_TYPE_TXT, 'orcunitfunc.txt'), \
                     (FILE_TYPE_TXT, 'orcunitstrings.txt'), \
                     (FILE_TYPE_TXT, 'undeadunitfunc.txt'), \
                     (FILE_TYPE_TXT, 'undeadunitstrings.txt'), \
                     (FILE_TYPE_TXT, 'neutralunitfunc.txt'), \
                     (FILE_TYPE_TXT, 'neutralunitstrings.txt')]
        slk_multi.__init__(self, in_dir, out_dir, file_list)

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class slk_item(slk_multi):
    
    def __init__(self, in_dir, out_dir):
        file_list = [(FILE_TYPE_SLK, 'itemdata.slk'), \
                     (FILE_TYPE_TXT, 'itemfunc.txt'), \
                     (FILE_TYPE_TXT, 'itemstrings.txt')]
        slk_multi.__init__(self, in_dir, out_dir, file_list)
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------



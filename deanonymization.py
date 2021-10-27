import string
import random
import json
import time

replaceterm = [["[protocolo]", 0], ["[adesivo]", 0], ["[cpf]", 0], ["[atendente]", 1],
               ["[inicio_hora_att]", 0], ["[fim_hora_att]", 0], ["[sobrenome]", 0],
               ["[valor_monetario]", 0], ["[valor]", 0], ["[estado_civil]", 0],
               ["[servico_whatsapp]", 0], ["[servico_telcap]", 0], ["[servico_tel]", 0],
               ["[email]", 0], ["[local]", 0], ["[placa]", 0], ["[telefone]", 0],
               ["[periodo]", 0], ["[caracter]", 0], ["[quantidade]", 0],
               ["[dia_da_semana]", 0], ["[hora]", 0], ["[data]", 0], ["[marca]", 0],
               ["[modelo]", 0], ["[ano]", 0], ["[link]", 0], ["[categoria]", 0],
               ["[cliente]", 1], ["[nome]", 1]]

def default (o):
    if type(o) is datetime.datetime:
        return o.isoformat()

def strTimeProp (start, end, format, prop):
    stime = time.mktime(time.strptime(start, '%d/%m/%Y'))
    etime = time.mktime(time.strptime(end, '%d/%m/%Y'))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

def randomDate (start, end, prop, format):
    return strTimeProp(start, end, format, prop)

def create_value (key, old_values):
    old_value = ""
    if (len(old_values) > 0): old_value = old_values[-1]
    key_repeat = ["[inicio_hora_att]", "[fim_hora_att]", "[servico_whatsapp]", "[servico_telcap]", "[servico_tel]", "[local]", "[categoria]", "[link]"]

    arquivo = open("/content/names_pt-br_new.json", "r", encoding='utf-8')
    names = json.load(arquivo)
    arquivo.close()

    arquivo = open("/content/listadesobrenomesbrasileiros.json", "r", encoding='utf-8')
    lastnames = json.load(arquivo)
    arquivo.close()

    value = ""
    iteration = 0
    if (key not in key_repeat): value = old_value
    while (((value == old_value)and(key not in key_repeat))or
           ((value == "")and(key in key_repeat))and(iteration < 5)):
        value = ""
        if (key == "[protocolo]"):
            for i in range(20): value += str(random.randint(0, 9))

        elif (key == "[adesivo]"):
            for i in range(15): value += str(random.randint(0, 9))

        elif (key == "[cpf]"):
            for i in range(11): value += str(random.randint(0, 9))
            prob = random.random()
            if (prob <= 0.33): value = value[:3]+"."+value[3:6]+"."+value[6:9]+"-"+value[9:]
            elif (prob <= 0.66): value = value[:3]+" "+value[3:6]+" "+value[6:9]+" "+value[9:]

        elif (key == "[atendente]"):
            gender = names[1][names[0].index(old_value)]
            index = random.randint(0, len(names[0])-1)
            while(int(names[1][index]) != gender): index = random.randint(0, len(names[0])-1)
            value = names[0][index]

        elif (key == "[hora]"):
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            if (hour < 10): value = "0"+str(hour)
            else: value = str(hour)
            if (minute < 10): value += ":0"+str(minute)
            else: value += ":"+str(minute)
            prob = random.random()
            if (prob > 0.5):
                second = random.randint(0, 59)
                if (second < 10): value += ":0"+str(second)
                else: value += ":"+str(second)

        elif (key == "[data]"):
            start = "01/01/2017"
            end = "01/09/2021"
            prob = random.random()
            format = '%d/%m/%Y %I:%M'
            if (prob <= 0.16): format = '%d/%m/%Y'
            elif (prob <= 0.33): format = '%d/%m'
            elif (prob <= 0.49): format = '%d-%m-%Y %I:%M'
            elif (prob <= 0.66):  format = '%d-%m-%Y'
            elif (prob <= 0.82):  format = '%d-%m'
            value = randomDate(start, end, random.random(), format)

        elif (key == "[sobrenome]"):
            for i in range(random.randint(1, 5)):
                value += lastnames[random.randint(0, len(lastnames)-1)]+" "
            value = value[:len(value)-1]

        elif (key == "[inicio_hora_att]"): value = "08:00"
        elif (key == "[fim_hora_att]"): value = "22:00"

        elif ((key == "[valor_monetario]")or(key == "[valor]")):
            valueint = random.randint(0, 999)
            valuefloat = random.randint(0, 99)
            if (valuefloat < 10): valuefloat = "0"+str(valuefloat)
            else: valuefloat = str(valuefloat)
            prob = random.random()
            if (prob <= 0.2): value = str(valueint)+" reais"
            elif (prob <= 0.4): value = "R$"+str(valueint)
            elif (prob <= 0.6): value = "R$"+str(valueint)+","+valuefloat
            elif (prob <= 0.8): value = str(valueint)+","+valuefloat+" reais"
            else: value = str(valueint)

        elif (key == "[estado_civil]"):
            prob = random.random()
            if (prob <= 0.2): value = "Solteir"
            elif (prob <= 0.4): value = "Casad"
            elif (prob <= 0.6): value = "Separad"
            elif (prob <= 0.8): value = "Divorciad"
            else: value = "Viúv"
            gender = random.sample([0, 1], k=1)[0]
            if (gender == 1): value += "a"
            else: value += "o"

        elif (key == "[servico_whatsapp]"): value = "3003-4475"
        elif (key == "[servico_telcap]"): value = "4020-2227"
        elif (key == "[servico_tel]"): value = "0800 030 2227"

        elif (key == "[email]"):
            dominio = ["yahoo.com.br", "gmail.com", "hotmail.com", "live.com"]
            value = names[0][random.randint(0, len(names[0])-1)].lower()+str(random.randint(1, 99))+"@"
            value += dominio[random.randint(0, len(dominio)-1)]

        elif (key == "[periodo]"):
            valueint = random.randint(0, 99)
            value = str(valueint)
            prob = random.random()
            if (prob <= 0.17): value += " minuto"
            elif (prob <= 0.34): value += " hora"
            elif (prob <= 0.50): value += " hr"
            elif (prob <= 0.67): value += " dia"
            elif (prob <= 0.83): value += " semana"
            else: value += " mes"
            if (valueint > 1):
                if (prob > 0.83):  value += "es"
                else: value += "s"

        elif (key == "[quantidade]"): value = str(random.randint(0, 99))
        elif (key == "[caracter]"): value = str(string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)])

        elif (key == "[dia_da_semana]"):
            weekday = ["domingo", "Domingo", "sábado", "sabado", "Sábado", "Sabado", "Segunda-feira", "Segunda-Feira", "segunda-feira", "segunda", "segunda feira", "Terça-feira", "Terça-Feira", "terça-feira", "terça", "terça feira", "Quarta-feira", "Quarta-Feira", "quarta-feira", "quarta", "quarta feira", "Quinta-feira", "Quinta-Feira", "quinta-feira", "quinta", "quinta feira", "Sexta-feira", "Sexta-Feira", "sexta-feira", "sexta", "sexta feira"]
            value = random.sample(weekday, k=1)[0]

        elif (key == "[local]"): value = old_value
        elif (key == "[categoria]"): value = old_value

        elif (key == "[modelo]"):
            modelos = ["Gol", "Uno", "Palio", "CrossFox", "Siena", "Celta", "Voyage", "HB20", "Corsa Sedan", "Onix", "Sandero", "Fiesta", "Cobalt", "Ka", "Corolla", "Civic", "Punto", "Fit", "Spin", "C3", "Cruze Sedan", "Logan", "Agile", "City", "Idea", "March", "Fiesta Sedan", "Space Fox", "Cruze HB", "Focus", "Versa", "i30", "Etios HB", "Doblò", "Golf", "Polo Sedan", "Palio Weekend", "Livina", "Fluence", "Bravo", "New Fiesta", "Jetta", "C3 Picasso", "Etios Sedan", "Polo", "Focus Sedan"]
            value = random.sample(modelos, k=1)[0]
            if (random.random() >= 0.5): value = value.lower()

        elif (key == "[marca]"):
            marcas = ["Chevrolet", "Volkswagen", "Fiat", "Renault", "Ford", "Toyota", "Hyundai", "Jeep", "Honda", "Nissan", "Citroën", "Mitsubishi", "Peugeot", "Chery", "BMW", "Mercedes-Benz", "Kia", "Audi", "Volvo", "Land Rover"]
            value = random.sample(marcas, k=1)[0]
            if (random.random() >= 0.5): value = value.lower()

        elif (key == "[ano]"): value = random.sample(["2017", "2018", "2019", "2020", "2021"], k=1)[0]
        elif (key == "[link]"): value = old_value

        elif (key == "[placa]"):
            prob = random.random()
            if (prob <= 0.5):
                for i in range(3): value += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()
                for i in range(4): value += str(random.randint(0, 9))
                prob = random.random()
                if (prob <= 0.6):
                    if (prob <= 0.2): value = value[:3]+" "+value[3:]
                    elif (prob <= 0.4): value = value[:3]+"-"+value[3:]
                else: value = value[:4]+string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].upper()+value[5:]
            else:
                for i in range(3): value += string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].lower()
                for i in range(4): value += str(random.randint(0, 9))
                prob = random.random()
                if (prob <= 0.6):
                    if (prob <= 0.2): value = value[:3]+" "+value[3:]
                    elif (prob <= 0.4): value = value[:3]+"-"+value[3:]
                else: value = value[:4]+string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)].lower()+value[5:]

        elif (key == "[telefone]"):
            for i in range(11): value += str(random.randint(0, 9))
            prob = random.random()
            if (prob <= 0.11): value = "0"+value
            elif (prob <= 0.22): value = "("+value[:2]+") "+value[2:7]+"-"+value[7:]
            elif (prob <= 0.33): value = "("+value[:2]+") "+value[2:7]+" "+value[7:]
            elif (prob <= 0.44): value = value[:2]+" "+value[2:7]+" "+value[7:]
            elif (prob <= 0.55): value = value[:2]+" "+value[2:7]+"-"+value[7:]
            elif (prob <= 0.66): value = value[:2]+"-"+value[2:7]+"-"+value[7:]
            elif (prob <= 0.77): value = value[2:7]+" "+value[7:]
            elif (prob <= 0.88): value = value[2:7]+"-"+value[7:]
            else: value = "("+value[:2]+") "+value[2:]

        elif ((key == "[cliente]")or(key == "[nome]")):
            gender = names[1][names[0].index(old_value)]
            index = random.randint(0, len(names[0])-1)
            while(int(names[1][index]) != gender): index = random.randint(0, len(names[0])-1)
            value = names[0][index]

        iteration += 1
    return value

def order_dialog (dialog):
    result = {}
    result["id"] = dialog["id"]
    result["dialog_domain"] = dialog["dialog_domain"]
    result["turns"] = []

    for turn in dialog["turns"]:
        new_turn = {}
        new_turn["speaker"] = turn["speaker"]
        new_turn["utterance"] = turn["utterance"]
        new_turn["utterance_delex"] = turn["utterance_delex"]
        if ("intent" in turn.keys()): new_turn["intent"] = turn["intent"]
        if ("action" in turn.keys()): new_turn["action"] = turn["action"]
        new_turn["slot-values"] = turn["slot-values"]
        new_turn["turn-num"] = turn["turn-num"]
        result["turns"].append(new_turn)
    return result

def fill_ontology (data):
    slot_values = {}
    action = []
    intent = []

    for item in data["dialogs"]:
        for turn in item["turns"]:
            if "action" in turn.keys():
                acts = turn["action"].replace("][", ", ").replace("[", "").replace("]", "").split(", ")
                for value in acts:
                    if (str("["+value+"]") not in action): action.append(str("["+value+"]"))
                
            elif "intent" in turn.keys():
                ints = turn["intent"].replace("][", ", ").replace("[", "").replace("]", "").split(", ")
                for value in ints:
                    if (str("["+value+"]") not in intent): intent.append(str("["+value+"]"))

            for key in turn["slot-values"].keys():
                if (key not in slot_values.keys()): slot_values[key] = []
                if isinstance(turn["slot-values"][key], list):
                    for value in turn["slot-values"][key]:
                        if (value not in slot_values[key]):
                            slot_values[key].append(value)
                else:
                    if (turn["slot-values"][key] not in slot_values[key]):
                        slot_values[key].append(turn["slot-values"][key])

    data["ontology"]["slot-values"] = slot_values
    data["ontology"]["intents"] = intent
    data["ontology"]["actions"] = action
    return data

def anonymization (sentence, context_variables, deanony):
    global replaceterm
    new_context = context_variables.copy()
    delex = sentence

    try:
        with open('patterns.json') as filep:
            patterns = json.load(filep)
            for key in patterns.keys():
                for pattern in patterns[key]:
                    key_context = key[0].replace("[", "").replace("]", "")
                    value = re.compile(pattern).findall(delex)[0]
                    delex = re.sub(pattern, key, delex)
                    new_context[key_context] = value
            try:
                with open('names_pt-br.json') as filen:
                    names = json.load(filen)[0]
                    for name in names:
                        delex = delex.replace(name, "[nome]")
                        new_context["nome"] = name
            except: delex = sentence
    except: delex = sentence

    original = sentence
    if (deanony):
        original = delex
        for key in replaceterm:
            while key[0] in original:
                key_context = key[0].replace("[", "").replace("]", "")
                value = create_value(key, selected_values[key[0]])
                if ((key[1] == 1)and(key_context in new_context.keys())):
                    value = new_context[key_context]
                new_context[key_context] = value
                original = original.replace(key, value, 1)

    return delex, original, new_context

def deanonymization (data, swap = False):
    global replaceterm
    augmented = {}
    augmented["ontology"] = data["ontology"].copy()
    augmented["dialogs"] = []

    selected_values_original = {}
    for key in replaceterm: selected_values_original[key[0]] = []

    static_data_original = {}
    for key in replaceterm:
        if (key[1] == 1): static_data_original[key[0]] = None

    for dialog in data["dialogs"]:
        selected_values = selected_values_original.copy()
        frequency = random.randint(4, 14)
        if (swap): frequency = 1

        for i in range(frequency):
            new_dialog = dialog.copy()
            if (swap == False):
                if ("-" in str(new_dialog["id"])):
                    new_dialog["id"] = new_dialog["id"].replace("-", "-"+str(i)+"-")
                else: new_dialog["id"] = str(i+1)+"-"+str(new_dialog["id"])
            new_dialog["turns"] = new_dialog["turns"].copy()
            static_data = static_data_original.copy()

            for turn in new_dialog["turns"]:
                turn["utterance"] = turn["utterance_delex"]
                turn["slot-values"] = turn["slot-values"].copy()

                for key in replaceterm:
                    if (key[0] in turn["utterance"]):
                        for occurrence in range(turn["utterance"].count(key[0])):
                            value = None
                            if isinstance(turn["slot-values"][key[0].replace("[", "").replace("]", "")], list):
                                selected_values[key[0]].append(turn["slot-values"][key[0].replace("[", "").replace("]", "")][occurrence])
                            else: selected_values[key[0]].append(turn["slot-values"][key[0].replace("[", "").replace("]", "")])

                            if (key[1] == 0): value = create_value(key[0], selected_values[key[0]])
                            else:
                                if (static_data[key[0]] == None):
                                    value = create_value(key[0], selected_values[key[0]])
                                    static_data[key[0]] = value
                                else: value = static_data[key[0]]

                            turn["utterance"] = turn["utterance"].replace(key[0], value, 1)
                            if isinstance(turn["slot-values"][key[0].replace("[", "").replace("]", "")], list):
                                turn["slot-values"][key[0].replace("[", "").replace("]", "")][occurrence] = value
                            else: turn["slot-values"][key[0].replace("[", "").replace("]", "")] = value

            augmented["dialogs"].append(order_dialog(new_dialog))
    return augmented

if __name__ == '__main__':
    filename = str(input("Filename: "))
    swap = int(input("Swap? (1 = Yes; 0 = No): "))
    if (swap == 1): swap = True
    else: swap = False

    arquivo = open(filename, "r", encoding='utf-8')
    data = json.load(arquivo)
    arquivo.close()

    result = deanonymization(data, swap)
    result = fill_ontology(result)
    with open("deanony.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(result, indent=2, default=default, ensure_ascii=False))
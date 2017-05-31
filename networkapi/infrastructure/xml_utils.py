# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from xml.dom import InvalidCharacterErr
from xml.dom.minicompat import StringTypes
from xml.dom.minidom import *


class XMLError(Exception):

    """Representa um erro ocorrido durante o marshall ou unmarshall do XML."""

    def __init__(self, cause, message):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Erro ao criar ou ler o XML: Causa: %s, Mensagem: %s' % (
            self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class InvalidNodeNameXMLError(XMLError):

    """Nome inválido para representá-lo como uma TAG de XML."""

    def __init__(self, cause, message):
        XMLError.__init__(self, cause, message)


class InvalidNodeTypeXMLError(XMLError):

    """Tipo inválido para o conteúdo de uma TAG de XML."""

    def __init__(self, cause, message):
        XMLError.__init__(self, cause, message)


def _add_text_node(value, node, doc):
    if value is None:
        return

    if not isinstance(value, StringTypes):
        text = '%s' % unicode(value)
    else:
        text = r'%s' % value.replace('%', '%%')

    try:
        textNode = doc.createTextNode(text)
        node.appendChild(textNode)
    except TypeError, t:
        raise InvalidNodeTypeXMLError(
            t, u'Conteúdo de um Nó do XML com tipo de dado inválido: %s ' % value)


def _add_list_node(nodeName, list, parent, doc):
    if list:
        for value in list:
            node = doc.createElement(nodeName)
            parent.appendChild(node)
            if isinstance(value, dict):
                _add_nodes_to_parent(value, node, doc)
            else:
                _add_text_node(value, node, doc)
    else:
        node = doc.createElement(nodeName)
        parent.appendChild(node)
        _add_text_node('', node, doc)


def _add_nodes_to_parent(map, parent, doc):
    if map is None:
        return

    for key, value in map.iteritems():
        try:
            if isinstance(value, dict):
                node = doc.createElement(key)
                parent.appendChild(node)
                _add_nodes_to_parent(value, node, doc)
            elif isinstance(value, type([])):
                _add_list_node(key, value, parent, doc)
            else:
                node = doc.createElement(key)
                parent.appendChild(node)
                _add_text_node(value, node, doc)

        except InvalidCharacterErr, i:
            raise InvalidNodeNameXMLError(
                i, u'Valor inválido para nome de uma TAG de XML: %s' % key)


def dumps(map, root_name, root_attributes=None):
    """Cria um string no formato XML a partir dos elementos do map.

    Os elementos do mapa serão nós filhos do root_name.

    Cada chave do map será um Nó no XML. E o valor da chave será o conteúdo do Nó.

    Throws: XMLError, InvalidNodeNameXMLError, InvalidNodeTypeXMLError
    """
    xml = ''
    try:
        implementation = getDOMImplementation()
    except ImportError, i:
        raise XMLError(i, u'Erro ao obter o DOMImplementation')

    doc = implementation.createDocument(None, root_name, None)

    try:
        root = doc.documentElement

        if (root_attributes is not None):
            for key, value in root_attributes.iteritems():
                attribute = doc.createAttribute(key)
                attribute.nodeValue = value
                root.setAttributeNode(attribute)

        _add_nodes_to_parent(map, root, doc)

        xml = doc.toxml('UTF-8')
    except InvalidCharacterErr, i:
        raise InvalidNodeNameXMLError(
            i, u'Valor inválido para nome de uma TAG de XML: %s' % root_name)
    finally:
        doc.unlink()

    return xml


def dumps_networkapi(map, version='1.0'):
    return dumps(map, 'networkapi', {'versao': version})


def _create_childs_map(parent, force_list):
    if parent is None:
        return None

    if parent.hasChildNodes():
        childs = parent.childNodes
        childs_map = dict()
        childs_values = []
        for i in range(childs.length):
            child = childs.item(i)
            if child.nodeType == Node.ELEMENT_NODE:
                if child.nodeName in childs_map:
                    child_value = _create_childs_map(child, force_list)
                    if child_value is not None:
                        value = childs_map[child.nodeName]
                        if not isinstance(value, type([])):
                            value = [value]
                        value.append(child_value)
                        childs_map[child.nodeName] = value
                elif child.nodeName in force_list:
                    child_value = _create_childs_map(child, force_list)
                    if child_value is None:
                        child_value = []
                    else:
                        child_value = [child_value]
                    childs_map[child.nodeName] = child_value
                else:
                    childs_map[child.nodeName] = _create_childs_map(
                        child, force_list)
            elif child.nodeType == Node.TEXT_NODE or child.nodeType == Node.CDATA_SECTION_NODE:
                if child.data.strip() != '':
                    childs_values.append(child.data.replace('%%', '%'))

        if len(childs_values) == 0 and len(childs_map) == 0:
            return None
        if len(childs_values) != 0 and len(childs_map) != 0:
            childs_values.append(childs_map)
            return childs_values
        if len(childs_values) != 0:
            if len(childs_values) == 1:
                return childs_values[0]
            return childs_values
        return childs_map
    elif parent.nodeType == Node.TEXT_NODE or parent.nodeType == Node.CDATA_SECTION_NODE:
        if parent.data.strip() != '':
            return parent.data

    return None


def loads(xml, force_list=None):
    """Cria um dict com os dados do element root.

    O dict terá como chave o nome do element root e como valor o conteúdo do element root.
    Quando o conteúdo de um element é uma lista de Nós então o valor do element será
    um dict com uma chave para cada nó.
    Entretanto, se existir nós, de um mesmo pai, com o mesmo nome, então eles serão
    armazenados uma mesma chave do dict que terá como valor uma lista.

    Se o element root tem atributo, então também retorna um dict com os atributos.

    Throws: XMLError
    """
    if force_list is None:
        force_list = []

    try:
        doc = parseString(xml)
    except Exception, e:
        raise XMLError(e, u'Falha ao realizar o parse do xml.')

    root = doc.documentElement

    map = dict()
    attrs_map = dict()

    if root.hasAttributes():
        attributes = root.attributes
        for i in range(attributes.length):
            attr = attributes.item(i)
            attrs_map[attr.nodeName] = attr.nodeValue

    map[root.nodeName] = _create_childs_map(root, force_list)

    return map, attrs_map


if __name__ == '__main__':

    map, attrs_map = loads('<teste/>')
    print map

    list = [{'id': None}, {'id': (2, 6)}]
    map = {'ambiente': list}
    xml = dumps(map, 'networkapi', {'versao': '1.0'})
    print xml

    map, attrs_map = loads(xml)
    print map

    xml = '<?xml version="1.0" encoding="UTF-8"?><networkapi versao="1.0"><!--Comentario--><ambiente><id><!--Comentario--></id></ambiente><ambiente><id>3<teste>geovana</teste>2</id></ambiente></networkapi>'
    map, attrs_map = loads(xml)
    print map

    xml = '<?xml version="1.0" encoding="UTF-8"?><networkapi versao="1.0"><!--Comentario--><ambiente><id><!--Comentario--></id></ambiente><ambiente><id>3 2 5</id></ambiente></networkapi>'
    map, attrs_map = loads(xml)
    print map

    xml = dumps(map, 'networkapi', attrs_map)
    print xml

    xml = dumps(None, 'networkapi', {'versao': '1.0'})
    print xml

    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <networkapi versao="1.0">
    <equipamento>
        <id_tipo_equipamento>1</id_tipo_equipamento>
        <id_modelo>teste</id_modelo>
        <nome>teste</nome>
        <id_grupo>teste</id_grupo>
    </equipamento>
    </networkapi>"""

    map, attrs_map = loads(xml)

    print map

    print dumps(map, 'networkapi', attrs_map)

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<networkapi versao="1.0">
<equipamento>
<id ></id>
</equipamento>
<equipamento_grupo>
<id></id>
</equipamento_grupo>
</networkapi>
"""

    map, attrs_map = loads(xml)

    print map

    print dumps(map, 'networkapi', attrs_map)

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<networkapi versao="1.0">
    <x/>
</networkapi>
"""

    map, attrs_map = loads(xml)

    print map

    print dumps(map, 'networkapi', attrs_map)

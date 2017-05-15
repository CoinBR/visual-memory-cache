# Memory Cache Simulator
# Tested in: Python 3.5.1
# Author: Pedro "Coin" Duarte <coinbr@gmail.com>
#
#
# DO WHAT THE FUCK YOU WANT TO BUT IT'S NOT MY FAULT PUBLIC LICENSE
# Version 1, October 2013
#
# Copyright © 2013 Ben McGinnes <ben@adversary.org>
#
# Everyone is permitted to copy and distribute verbatim or modified copies
# of this license document, and changing it is allowed as long as
# the name is changed.
#
# DO WHAT THE FUCK YOU WANT TO BUT IT'S NOT MY FAULT PUBLIC LICENSE TERMS
# AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
#
# 1. Do not hold the author(s), creator(s), developer(s) or distributor(s)
# liable for anything that happens or goes wrong with your use of the work.

import random
import string
import json

from collections import deque, OrderedDict

import matplotlib.pyplot as plt


def hp(stuff):
    print()
    print(70*'>')
    print(stuff)
    print(70*'<')


class Memory:

    def __init__(self, size=1024):

        self.size = size
        # self.items = [random.choice(string.ascii_letters) for i in range(size)]
        self.items = {}

    def read(self, address):
        if address not in self.items:
            self.write(address, random.choice(string.ascii_letters))
        else:
            self.items[address]['highlight'] = True
        return self.items[address]

    def write(self, address, value):
        self._check_and_enforce_limit()
        self.items[address] = {'value': value, 'highlight': True}
        return value

    def clear_highlights(self):
        for item in self.items:
            self.items[item].pop('highlight', None)

    def _check_and_enforce_limit(self):

        if len(self.items) >= self.size:
            self.items.popitem()

    def _to_json(self):
        return sorted(self.items.items())


class Block(json.JSONEncoder):

    def __init__(self, n_layers=1, n_words=1, index_bin=str(0), memory=Memory()):

        self.n_layers = n_layers
        self.layers = [Layer(rank, n_words, index_bin, memory)
                       for rank in range(n_layers)]
        self.memory = memory
        self.index_bin = index_bin

    def _to_json(self):
        return {'layers': [layer._to_json() for layer in self.layers]}

    def clear_highlights(self):
        for layer in self.layers:
            layer.highlight = False

    def access_address(self, address_tag, word=0):
        """
        >>> b = Block(4)
        >>> b.fix_ranks(3)
        [0, 1, 2, 3]
        >>> b.access_address('F')
        False
        >>> b.fix_ranks(3)
        [3, 0, 1, 2]
        >>> b.access_address('F')
        True
        >>> b.fix_ranks(3)
        [3, 0, 1, 2]
        """

        for layer in self.layers:
            rank = layer.access_address(address_tag, word)
            if rank is not None:
                self.fix_ranks(rank)
                return True

        self._process_miss(address_tag)
        return False

    def write(self, address_tag, word_int=0, op='w'):

        for layer in self.layers:
            rank = layer.try_write(address_tag, word_int, op)
            if rank is not None:
                self.fix_ranks(rank)
                return

        self.get_layer_by_rank(self.n_layers - 1).write(address_tag,
                                                        word_int, op)

    def get_layer_by_rank(self, rank):
        """
        >>> Block().get_layer_by_rank(0).rank
        0
        >>> Block(3).get_layer_by_rank(2).rank
        2
        >>> b = Block(8)
        >>> b.get_layer_by_rank(7).rank
        7
        >>> b.get_layer_by_rank(5).rank
        5

        """

        if rank >= self.n_layers or rank < 0:
            raise AttributeError('Rank out of bounds')

        for layer in self.layers:
            if int(layer.rank) == int(rank):
                return layer

        raise AttributeError('Layer not found (Rank {0})'.format(rank))

    def _process_miss(self, address_tag, word=0, index=str(0)):

        rank = 0
        self.get_layer_by_rank(rank).process_miss(address_tag, word)
        self.fix_ranks(rank)

    def fix_ranks(self, rank):
        """
        >>> b = Block(8)
        >>> [layer.rank for layer in b.layers]
        [0, 1, 2, 3, 4, 5, 6, 7]
        >>> b.fix_ranks(5)
        [0, 1, 2, 3, 4, 7, 5, 6]
        """

        top_rank = self.n_layers - 1
        if rank < top_rank:
            new_top_layer = self.get_layer_by_rank(rank)
            for i in range(rank + 1, self.n_layers):
                self.get_layer_by_rank(i).rank -= 1

            new_top_layer.rank = top_rank

        return [layer.rank for layer in self.layers]


class Layer:

    def __init__(self, rank=0, n_words=1, index_bin=str(0), memory=Memory()):

        self._pristine = True
        self.dirty = False
        self._address_tag = None
        self.rank = rank
        self.n_words = n_words
        self.words = [0 for i in range(n_words)]
        self.index_bin = index_bin
        self.memory = memory
        self.highlight = False

    def _to_json(self):

        rtrn = {
                'valid': int(not self._pristine),
                'dirty': int(self.dirty),
                'rank': self.rank,
                'words': self.words,
                'tag': self._address_tag
               }
        if self.highlight:
            rtrn['highlight'] = True
        return rtrn

    def access_address(self, address_tag, word=0, index=str(0)):
        # Access a memory Address. If in cache, returns Layer Rank #
        """
        >>> c = Cache(2, 1, 4)

        >>> c.read('A0')
        >>> print(c)
        0 / 1

        >>> c.read('A2')
        >>> print(c)
        0 / 2

        >>> c.read('A4')
        >>> print(c)
        0 / 3

        >>> c.read('A2')
        >>> print(c)
        1 / 4

        >>> c.read('A6')
        >>> print(c)
        1 / 5

        >>> c.read('A4')
        >>> print(c)
        2 / 6

        >>> c.read('A2')
        >>> print(c)
        3 / 7

        >>> c.read('A0')
        >>> print(c)
        4 / 8

        >>> c.read('B1')
        >>> print(c)
        4 / 9

        >>> c.read('B5')
        >>> print(c)
        4 / 10

        >>> c.read('B7')
        >>> print(c)
        4 / 11

        >>> c.read('B3')
        >>> print(c)
        4 / 12

        >>> c.read('B9')
        >>> print(c)
        4 / 13
        """

        if self._pristine:
            self._pristine = False
            return None

        elif self._address_tag != address_tag:
            return None

        self.highlight = True
        return self.rank

    def try_write(self, address_tag, word_int=0, op='w'):

        if self._address_tag != address_tag:
            return None

        self.write(address_tag, word_int, op)
        return self.rank

    def write(self, address_tag, word_int=0, op='w'):

        self.highlight = True

        word_bin = bin(word_int)[2:]
        value = random.choice(string.ascii_letters)
        full_address = ''.join((address_tag, self.index_bin, word_bin))

        self._address_tag = address_tag
        # self.fill_words_from_memory(address_tag, word_bin)
        self.words[word_int] = value

        if op == 'w':
            self.memory.write(full_address, value)
        else:
            self.dirty = True

    def _gen_all_possible_words(self):
        if self.n_words == 1:
            return ''

        n_chars = len(bin(self.n_words - 1)[2:])

        return [bin(i)[2:].zfill(n_chars)
                for i in range(self.n_words)]

    def _copy_back_fix(self, word):
        if self.dirty:
            full_address = ''.join((self._address_tag, self.index_bin,
                                   bin(word)[2:]))
            self.memory.write(full_address, self.words[word])

    def process_miss(self, address_tag, word):

        self.highlight = True
        self._copy_back_fix(word)
        self._address_tag = address_tag
        self.fill_words_from_memory(address_tag, word)

    def fill_words_from_memory(self, address_tag, word):
        self.words = [self.memory.read(''.join(
            (address_tag, self.index_bin, w, )))['value']
                      for w in self._gen_all_possible_words()]

    def _fetch_instruction():
        pass

    def __str__(self):

        if self._pristine:
            return 'Never Acessed'
        return self._address_tag

    def __repr__(self):
        return self.__str__()


class Cache:

    def __init__(self, n_blocks=4, n_words=1, n_layers=1, address_size=32,
                 method='r'):

        if (n_blocks < 1
                or not isinstance(n_blocks, int)):
            raise ValueError('Invalid Cache Size')

        self.n_blocks = n_blocks
        self.n_layers = n_layers
        self.address_size = address_size
        self.index_size = self._get_n_bits_to_reserve(n_blocks)
#        self.memory = Memory(2 ** address_size - 1)
        # not really a memory, just a fake summary to print
        self.memory = Memory(max(256, n_blocks * n_layers * n_words * 2))
        self.method = method

        if n_words == 1:
            self.words_size = 0
            self.n_words = 0
        else:
            self.words_size = self._get_n_bits_to_reserve(n_words)
            self.n_words = n_words

        self.reset()

    def reset(self):
        self.n_reads = 0
        self.n_hits = 0
        self._blocks = [Block(self.n_layers, self.n_words,
                              bin(i)[2:].zfill(self.index_size),
                              self.memory)
                        for i in range(self.n_blocks)]

    def _hex_to_bin(self, value):
        """
        >>> Cache(8)._hex_to_bin('C01')
        '00000000000000000000110000000001'

        >>> Cache(8)._hex_to_bin('0')
        '00000000000000000000000000000000'


        >>> Cache(8)._hex_to_bin('047A')
        '00000000000000000000010001111010'

        >>> Cache(8)._hex_to_bin('FFFFFFFF1') # above address size
        Traceback (most recent call last):
        ...
        ValueError: Address Out of Range
        """

        value = bin(int(value, 16))[2:].zfill(self.address_size)
        if len(value) > self.address_size:
            raise ValueError('Address Out of Range')

        return value

    def _get_word(self, address):
        """
        >>> c = Cache(8)
        >>> c._get_index(c._hex_to_bin('A')) # (1010)
        '010'
        >>> c._get_index(c._hex_to_bin('C01')) # (110000000001)
        '001'

        >>> c = Cache(15)
        >>> c._get_index(c._hex_to_bin('ABC')) # (101010111100)
        '1100'
        >>> c._get_index(c._hex_to_bin('A0F')) # (101000001111)
        '1111'
        """
        return address[self.address_size - self.words_size:]

    def _get_index(self, address):
        """
        >>> c = Cache(8)
        >>> c._get_index(c._hex_to_bin('A')) # (1010)
        '010'
        >>> c._get_index(c._hex_to_bin('C01')) # (110000000001)
        '001'

        >>> c = Cache(15)
        >>> c._get_index(c._hex_to_bin('ABC')) # (101010111100)
        '1100'
        >>> c._get_index(c._hex_to_bin('A0F')) # (101000001111)
        '1111'
        """
        return address[self.address_size - self.index_size - self.words_size:
                       self.address_size - self.words_size]

    def _get_tag(self, address):
        """
        >>> c = Cache(8)
        >>> c._get_tag(c._hex_to_bin('A')) # (1010)
        '00000000000000000000000000001'
        >>> c._get_tag(c._hex_to_bin('C01')) # (110000000001)
        '00000000000000000000110000000'

        >>> c = Cache(15)
        >>> c._get_tag(c._hex_to_bin('ABC')) # (101010111100)
        '0000000000000000000010101011'
        >>> c._get_tag(c._hex_to_bin('A0F')) # (101000001111)
        '0000000000000000000010100000'
        """
        return address[:self.address_size - self.index_size - self.words_size]

    def _split_address(self, hex_address):
        address = self._hex_to_bin(hex_address)
        return (self._get_tag(address), self._get_index(address),
                self._get_word(address))

    def _get_block(self, hex_address):
        index = self._get_index(self._hex_to_bin(hex_address))
        return self._blocks[int(index, 2)]

    def read(self, hex_address):
        """
        >>> c = Cache(4)
        >>> c.read('FFFFFFFF')
        >>> print(c)
        0 / 1
        >>> c.read('FFFFFFFF')
        >>> print(c)
        1 / 2
        >>> c.read('FFFFFFFF')
        >>> print(c)
        2 / 3
        >>> c.read('00000000')
        >>> c.read('00000333')
        >>> print(c)
        2 / 5
        >>> c.read('00000001')
        >>> c.read('00000333')
        >>> print(c)
        3 / 7
        >>> c.read('00000002')
        >>> c.read('00000332')
        >>> print(c)
        3 / 9

        # Same Block
        >>> c.read('00000006')
        >>> c.read('00000002')
        >>> print(c)
        3 / 11
        >>> c.read('00000002')
        >>> c.read('00000006')
        >>> print(c)
        4 / 13


        # Many layers and words
        # TODO

        """
        tag, index, word = self._split_address(hex_address)
        block = self._get_block(hex_address)
        self.n_hits += block.access_address(tag, word)
        self.n_reads += 1

    def write(self, hex_address):

        tag, index, word = self._split_address(hex_address)
        block = self._get_block(hex_address)
        block.write(tag, int(word, 2), self.method)

    def _clear_highlights(self):
        self.memory.clear_highlights()
        for block in self._blocks:
            block.clear_highlights()

    def process(self, op, address):
        self._clear_highlights()

        if op not in ('r', 'w', 'c', ):
            raise AttributeError('Cache Operation \'{0}\' is not\
                                 supported'.format(op))
        if op == 'r':
            self.read(address)
        else:
            self.write(address)


    def _get_n_bits_to_reserve(self, max_num):
        """ # of last bits reserved to determine memory group
        >>> Cache(8).index_size
        3
        >>> Cache(8).index_size
        3
        >>> Cache(12).index_size
        4
        >>> Cache(13).index_size
        4
        >>> Cache(63).index_size
        6
        >>> Cache(64).index_size
        6
        >>> Cache(65).index_size
        7
        >>> Cache(67).index_size
        7

        """

        power = 1
        while 2 ** power < max_num:
            power += 1

        return power

    def __str__(self):
        return '{0} / {1}'.format(self.n_hits, self.n_reads)


class Tracer:

    def __init__(self, cache, filename):
        self.cache = cache
        self.method = cache.method
        self.filename = filename
        self.reset()

    def reset(self):
        self.log = []
        self.requests = self._filter()
        self.cache.reset()

    def _readlines(self):
        with open('traces/{0}.trace'.format(self.filename)) as f:
            content = f.readlines()

        return [x.strip() for x in content]

    def _filter(self):
#        """
#        >>> Tracer(Cache(8), 'tst')._filter()
#        ['20d', '211', 'fafe', 'c01111', '0', '1', '2', '3', '4', '4', '5', '6']
#        """
        """
        >>> Tracer(Cache(8), 'tst')._filter()
        deque([('r', '20d'), ('r', '211'), ('r', 'fafe'), ('r', 'c01111'), ('r', '0'), ('r', '1'), ('r', '2'), ('r', '3'), ('r', '4'), ('r', '4'), ('r', '5'), ('r', '6')])
        """

        rtrn = deque([])
        for line in self._readlines():
            op_int = int(line[0])
            op_s = None
            address = line[2:]

            if op_int == 1 and not self.method == 'r':
                op_s = self.method

            elif op_int in (0, 2, ):
                op_s = 'r'

            if op_s:
                rtrn.append((op_s, address, ))

        return rtrn

    def _log_step(self):
        return {
            'cache': {
                'blocks': [block._to_json() for block in self.cache._blocks]
            },
            'memory': self.cache.memory._to_json(),
            # list(self.cache.memory.items.items())
            'rates': {
                'hits': self.cache.n_hits,
                'reads': self.cache.n_reads
            },
            'instruction': self.current_instruction,
            'last_step': False,
        }

    def trace(self):
        """
        >>> Tracer(Cache(8), 'tst').trace()
        '1 / 12'
        >>> Tracer(Cache(4, 4), 'tst').trace()
        '6 / 12'
        """

        while type(self.trace_step()) is not dict:
            pass

        return str(self.cache)

    def trace_step(self, log_step=False):

        op, address = self.requests.popleft()
        self.current_instruction = ' - '.join((op.upper(), address))
        if self.current_instruction[0] == 'C':
            self.current_instruction = 'W' + self.current_instruction[1:]
        self.cache.process(op, address)
        self.log.append((self.cache.n_hits, self.cache.n_blocks))
        if len(self.requests) <= 0:
            self.requests.append((op, address))
            r = self._log_step()
            r['last_step'] = True
            return r
        if log_step:
            return self._log_step()
        return True

def plot(tracer):

    plt.plot([entry[0] for entry in tracer.log])
    plt.xlabel('Accesses')
    plt.ylabel('Hits')
    plt.show()


if __name__ == "__main__":

    n_blocks = int(input("# of cache blocks: "))
    n_words = int(input("# of words in each block: "))
    n_layers = int(input("# of layers in each block: "))
    filename = input("trace file name: ")
    method = input("Method. (r)ead, (w)rite through or (c)opy back: ")
    if not method:
        method = 'r'

    cache = Cache(n_blocks, n_words, n_layers)
    tracer = Tracer(cache, filename)

    print('{0} ({1:.2f}%)'.format(tracer.trace(),
                                  tracer.cache.n_hits / tracer.cache.n_reads
                                  * 100))

#    with open('result.json', 'w') as fp:
#        json.dump(tracer.steps, fp)
#        fp.close()

    plot(tracer)
    input()

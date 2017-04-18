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


import matplotlib.pyplot as plt


class Block:

    def __init__(self, n_layers=1):

        self.n_layers = n_layers
        self.layers = [Layer(rank) for rank in range(n_layers)]

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
            rank = layer.access_address(address_tag)
            if rank is not None:
                self.fix_ranks(rank)
                return True

        self._process_miss(address_tag)
        return False


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


    def _process_miss(self, address_tag):

       rank = 0
       self.get_layer_by_rank(rank).process_miss(address_tag)
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

    def __init__(self, rank=0):

        self._pristine = True
        self._address_tag = None
        self.rank = rank

    def access_address(self, address_tag, word=0):
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

        return self.rank

    def process_miss(self, address_tag):
        self._address_tag = address_tag

    def _fetch_instruction():
        pass

    def __str__(self):

        if self._pristine:
            return 'Never Acessed'
        return self._address_tag

    def __repr__(self):
        return self.__str__()


class Cache:

    def __init__(self, n_blocks=4, n_words=1, n_layers=1, address_size=32):

        if (n_blocks < 1
                or n_blocks > 1024
                or not isinstance(n_blocks, int)):
            raise ValueError('Invalid Cache Size')

        self.n_blocks = n_blocks
        self.n_layers = n_layers
        self.memo_size = 2 ** n_blocks
        self.address_size = address_size
        self.index_size = self._get_n_bits_to_reserve(n_blocks)

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
        self._blocks = [Block(self.n_layers) for i in range(self.n_blocks)]

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
        address = self._hex_to_bin(hex_address)

        block = self._blocks[int(self._get_index(address), 2)]
        self.n_hits += block.access_address(self._get_tag(address),
                                            self._get_word(address))
        self.n_reads += 1

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
        self.filename = filename
        self.log = []

    def _readlines(self):
        with open('traces/{0}.trace'.format(self.filename)) as f:
            content = f.readlines()

        return [x.strip() for x in content]

    def _filter(self):
        """
        >>> Tracer(Cache(8), 'tst')._filter()
        ['20d', '211', 'fafe', 'c01111', '0', '1', '2', '3', '4', '4', '5', '6']
        """
        rtrn = []
        for line in self._readlines():
            if line[0] == '2':
                rtrn.append(line[2:])
        return rtrn

    def trace(self):
        """
        >>> Tracer(Cache(8), 'tst').trace()
        '1 / 12'
        >>> Tracer(Cache(4, 4), 'tst').trace()
        '6 / 12'
        """

        self.cache.reset()
        self.log = []

        for word in self._filter():
            self.cache.read(word)
            self.log.append((self.cache.n_hits,
                             self.cache.n_blocks))

        return str(self.cache)


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

    cache = Cache(n_blocks, n_words, n_layers)
    tracer = Tracer(cache, filename)

    print('{0} ({1:.2f}%)'.format(tracer.trace(),
                                  tracer.cache.n_hits / tracer.cache.n_reads
                                  * 100))
    plot(tracer)
    input()

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


class Block:

    def __init__(self, n_words=1):

        self._pristine = True
        self._address_tag = None

    def access_address(self, address_tag, word=0):
        # Access a memory Address. If in cache, returns True (hit)

        if self._pristine:
            self._pristine = False
            self._address_tag = address_tag
            return False

        elif self._address_tag != address_tag:
            self._address_tag = address_tag
            return False
        return True

    def _fetch_instruction():
        pass

    def __str__(self):

        if self._pristine:
            return 'Never Acessed'
        return self._address_tag

    def __repr__(self):
        return self.__str__()


class Cache:

    def __init__(self, n_blocks=4, n_words=1, address_size=32):

        if (n_blocks < 1
                or n_blocks > 1024
                or not isinstance(n_blocks, int)):
            raise ValueError('Invalid Cache Size')

        self.n_blocks = n_blocks
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
        self._blocks = [Block() for i in range(self.n_blocks)]

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
            self.log.append(str(self.cache))

        return str(self.cache)


if __name__ == "__main__":

    n_blocks = int(input("# of cache blocks: "))
    memo_size = int(input("# of memory words: "))
    filename = input("trace file name: ")

    cache = Cache(n_blocks, memo_size)
    tracer = Tracer(cache, filename)

    print(tracer.trace())
    input()

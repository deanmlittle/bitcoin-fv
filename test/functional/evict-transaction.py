#!/usr/bin/env python3
# Copyright (c) 2022 Dean Little
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""evicttransaction RPCs QA test.

# Tests the following RPCs:
#    - evicttransaction
"""
from decimal import Decimal

from test_framework.cdefs import ONE_KILOBYTE
from test_framework.test_framework import BitcoinTestFramework
from test_framework.mininode import COIN
from test_framework.util import *

class EvictTransactionsTest(BitcoinTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 4
        self.relayfee = Decimal(1) * ONE_KILOBYTE / COIN
        self.extra_args = [[],[],[],['-maxmempool=300', '-maxmempoolsizedisk=0', f"-minminingtxfee={self.relayfee}"
                                     , f"-mindebugrejectionfee={self.relayfee}"]]

    def run_test(self):
        # prepare some coins for multiple *rawtransaction commands
        self.nodes[0].generate(120)
        addr = self.nodes[0].getnewaddress()
        txId = self.nodes[0].sendtoaddress(addr, 10)
        self.sync_all()
        inputs = [
            {'txid': txId, 'vout': 1}
        ]
        outputs = {addr: 9.999999}
        rawtx_child = self.nodes[0].createrawtransaction(inputs, outputs)
        rawtx_child = self.nodes[0].signrawtransaction(rawtx_child)
        txId2 = self.nodes[0].sendrawtransaction(rawtx_child['hex'], True, False)
        # Evict a fake TX and expect a null result
        evicted = self.nodes[0].evicttransaction("1d1d4e24ed99057e84c3f80fd8fbec79ed9e1acee37da269356ecea000000000")
        assert_equal(evicted, {'evicted': []})
        # Evict the parent TX and expect to see it and its child removed
        evicted = self.nodes[0].evicttransaction(txId)
        assert_equal(evicted, {'evicted': [txId2, txId]})
        # Make sure mempool is empty
        mempool = self.nodes[0].getrawmempool()
        assert_equal(mempool, [])

if __name__ == '__main__':
    EvictTransactionsTest().main()

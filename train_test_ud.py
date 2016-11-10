#!/usr/bin/env python

import sys
import subprocess
import tempfile

TRAIN_LENGTH = 10
TEST_LENGTH = 40

NUM_SENTS = 6000 # limit the number of training sentences for efficiency

POS = 3
WORD = 1
HEAD = 6

PROG_DIR = './' # where fast_dep.o, rules_ud, etc exist

PROG = PROG_DIR + 'fast_dep.o'
RULES = PROG_DIR + 'rules_ud'
MAP = PROG_DIR + 'map_ud'
DEP_MAT = PROG_DIR + 'dep_matrix.txt' # seems useless?
D_RULES = PROG_DIR + 'dir_rules' # this also seems unused

class Data(object):
    def __init__(self, train_path, test_path):

        self.train = [s for s in self._conll_sentences(train_path)
                      if len(s) <= TRAIN_LENGTH]
        self.test = [s for s in self._conll_sentences(test_path) if len(s) <= TEST_LENGTH]

        self.train = self.train[:NUM_SENTS]

        self.words = tempfile.NamedTemporaryFile(delete=False)
        self.poses = tempfile.NamedTemporaryFile(delete=False)
        self.deps = tempfile.NamedTemporaryFile(delete=False)
        self.test_words = tempfile.NamedTemporaryFile(delete=False)
        self.test_poses = tempfile.NamedTemporaryFile(delete=False)
        self.test_deps = tempfile.NamedTemporaryFile(delete=False)

        self._output(self.words, self.poses, self.deps, self.train)
        self._output(self.test_words, self.test_poses, self.test_deps, self.test)

    def _conll_sentences(self, path):
        sentences = []
        sentence = []
        for line in open(path):
            line = line.strip()
            if line:
                sentence.append(line.split('\t'))
            elif sentence:
                sentences.append(sentence)
                sentence = []
        if sentence:
            sentences.append(sentence)
        return sentences

    def _output(self, words_o, poses_o, deps_o, sentences):
        for sentence in sentences:
            poses = [t[POS] for t in sentence]
            words = [t[WORD] for t in sentence]
            heads = [t[HEAD] for t in sentence]

            words_o.write(' '.join(words) + ' #\n')
            poses_o.write(' '.join(poses) + ' #\n')

            def zero_base(idx):
                if idx == '0': return len(heads)
                else: return str(int(idx) - 1)

            deps = ['%s-%s' % (zero_base(heads[i]), i) for i in range(len(heads))]
            deps_o.write(' '.join(deps) + '\n')

        words_o.flush()
        poses_o.flush()
        deps_o.flush()

'''Get Naseem et al style data from CoNLL format'''
def get_config(data, output):
    return (
        ('T', 10),
        ('count', 10000),
        ('beta', 'true'),
        ('deps', data.deps.name),
        ('poses', data.poses.name),
        ('words', data.words.name),
        ('test_deps', data.test_deps.name),
        ('test_poses', data.test_poses.name),
        ('test_words', data.test_words.name),
        ('alpha_0', 1),
        ('alpha_1', 10),
        ('hyp', 1),
        ('out_put', "/dev/null"),
        ('output_test', output),
        ('tag_set_map', MAP),
        ('rules', RULES),
        ('neg_rules', DEP_MAT),
        ('dir_rules', D_RULES),
        ('threshold', 0.8))

def evaluate(output):
    def read_results(path):
        results = []
        result = []
        for line in open(path):
            line = line.strip()
            if line:
                result.append(line)
            elif result:
                results.append(result)
                result = []
        if result:
            results.append(result)
        return results

    # deps may be ['2-1', '3-2', '0-3', '4-0']
    # extract ['4', '2', '3', '0']
    def heads(deps):
        def to_pair(d):
            items = d.split('-')
            head = items[0]
            dep = items[1]
            return (head, dep)
        arcs = [to_pair(d) for d in deps]
        arcs = sorted(arcs, key = lambda x: x[1])
        return [a[0] for a in arcs]

    def print_scores(results):
        toks = 0
        match = 0

        for result in results:
            gold = heads(result[1].split(' ')[1:])
            pred = heads(result[3].split(' ')[1:])

            for g, p in zip(gold, pred):
                if g == p:
                    match += 1
                toks += 1

        print
        print "Evaluating test sentences:"
        print "UAS: %s" % (float(match) / toks)
        print "total: %s" % toks
        print "correct: %s" % match

    results = read_results(output)
    print_scores(results)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "usage: %s train.conll test.conll output" % (sys.argv[0])
        exit()

    train_conll = sys.argv[1]
    test_conll = sys.argv[2]
    guess = sys.argv[3]

    config_file = tempfile.NamedTemporaryFile(delete=False)

    data = Data(train_conll, test_conll)

    config = get_config(data, guess)
    config_str = '\n'.join(['%s\t%s ' % (c[0], c[1]) for c in config])
    config_file.write(config_str)
    config_file.flush()

    subprocess.check_call([PROG, config_file.name])

    evaluate(guess)

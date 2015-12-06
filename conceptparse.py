import re
import ast
from nltk.corpus import stopwords


#############CONSTANTS###############
parseTreeFile = "Stanford CoreNLP\stanford-corenlp-full-2015-04-20\wordFile.txt.out"



#Reads each line of the output file, parsing the trees into single strings.
#Also adds lemmas of each, to replace actua wlord in parse tree later.
flatTrees = []
tree = ""
inTree = False
allLemmas = []
lemmas = {}
with open(parseTreeFile) as treeFile:
	for line in treeFile:
		line = line[:-1].strip()
		print line
		#Finds each lemma, and stores in list.
		if line.startswith("[Text="):
			origTerm = re.search("\[Text=(.*?) ", line)
			lemma = re.search("Lemma=(.*?) ", line)
			lemmas[origTerm.group(1)] = lemma.group(1)
		#Finds and stores each parse tree as single string.
		if line == "(ROOT":
			inTree = True
			#No more lemmas, since we're on to the tree. Reset.
			allLemmas.append(lemmas)
			lemmas = []
		if not line and inTree:
			flatTrees.append(tree)
			inTree = False
			tree = ""
		if inTree:
			tree += line

#Forms a tree (list of lists) from flat string
trees = []
for line in flatTrees:
	prepLine = line
	prepLine = re.sub("([() ])([^() ])", "\\1\"\\2", prepLine)	#add quotes
	prepLine = re.sub("([^() ])([() ])", "\\1\"\\2", prepLine)	#add quotes
	prepLine = re.sub("(\")([( ])", "\\1,\\2", prepLine)		#insert comma between elts
	prepLine = re.sub("(\))([( ])", "\\1,\\2", prepLine)		#insert comma after list
	tree = ast.literal_eval(prepLine)							#convert to list
	print tree
	trees.append(tree)

def replaceWithLemma(tree, lemmas):
	"""
	Replacing each word with its appropriate lemma in tree via recursion.
	args: tree (tuple)
	returns: tree (tuple)
	"""
	root = tree[0]
	branch = tree[1]
	branches = tree[1:]

	if type(branch) is str:			#end of branch
		lemma = lemmas[tree[1]]
		return (root, lemma)
	elif type(branch) is tuple:		#not end of branch
		#wrapper, since function in map only takes the iterable (so can't pass in lemmas)
		func = lambda tree: replaceWithLemma(tree, lemmas)
		#use map since could be multiple branches (multiple tuples)
		newTree = tuple([root] + map(func, branches))
		return newTree
	else:
		raise TypeError("Failed replacing words with respective lemmas since "+
						"input was not a tuple, or did not contain strings.")

lemmaTree = replaceWithLemma(trees[0], allLemmas[0])
print(lemmaTree)

def NPbigrams(tree):
	"""
	Creates bigrams (two word pair) of noun phrases (NPs) in tree via recursion.
	"""
	sw = set(stopwords.words("english"))
	bigrams = []
	NPs = findNPs(tree)

	for NP in NPs:
		print(NP)
		terms = NP[1:]
		nounTerms = []
		adjTerms = []
		afterNoun = False
		#sort into nouns and other terms
		for term in terms:
			if "NN" in term[0]:		#noun
				nounTerms.append(term[1])
				afterNoun = True
			elif term[1] in sw:		#stopword
				continue
			elif "JJ" == term[0]:	#adjective
				if afterNoun:
					continue	#these adj's have little effect
				else:
					adjTerms.append(term[1])
		#adj + noun bigrams
		for noun in nounTerms:
		 	for adj in adjTerms:
		 		bigram = [adj, noun]
		 		bigrams.append(bigram)
		#noun + noun bigrams
		if len(nounTerms) > 1:
			for i in range(len(nounTerms)-1):
			 	bigram = [nounTerms[i], nounTerms[i+1]]
			 	bigrams.append(bigram)
		elif len(nounTerms) == 1 and len(adjTerms) == 0:	#since if are adj's, then will form an
			bigram = [nounTerms[0]]							#adj group already containing noun.
			bigrams.append(bigram)

	for b in bigrams:
		print b

	bigrams = [b[0]+"_"+b[1] if len(b) == 2 else b[0] for b in bigrams]
	return bigrams


def findNPs(tree):
	"""
	Finds & returns list of NP subtrees in tree with at least one NN(S) as a subtree.
	"""
	root = tree[0]
	branch = tree[1]
	branches = tree[1:]

	if root == "NP":
		#if subtree root is NP, call findNPS on it.
		finalList = []
		for b in branches:
			finalList += findNPs(b)
		#if not nested NP, just return current NP
		return finalList if finalList else [tree]
	else:
		#search for NP in subtrees
		if type(branch) == str:		#end of branch, return empty list
			return []
		elif type(branch) == tuple:	#more subbranches to go
			finalList = []
			for b in branches:
				finalList += findNPs(b)
			return finalList
		else:
			raise TypeError("Failed to find NP bigrams since something in tree is"+
							"neither a tuple or a string")

bigrams = NPbigrams(lemmaTree)
print bigrams




def findVPBigrams(tree)
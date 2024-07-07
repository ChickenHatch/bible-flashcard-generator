import genanki
import random
import pandas as pd
import re
import numpy as np
import time

random.seed(7)
number = random.randrange(1 << 30, 1 << 31)

cardCount = 0

global decks 
decks = {}

def getBookDeck(bookName):
  if hasattr(decks, bookName):
    return decks[bookName]
  else:
    decks[bookName] = genanki.Deck(
    number,
    'Memorizing ' + bookName)
    return decks[bookName]

def createNote(prev, text, length, deck, tag, due):
  minWords = 7
  maxWords = 7
  if length == 'verse':
    minWords = 1
    maxWords = 3
  elif length == 'chapter':
    minwords = 12
    maxWords = 49
  global cardCount
  result = np.array(text.split(" "))
  groupingLen = 0
  groupWordsArray = []
  stuck = 0
  prevGroupingLen = 0
  while groupingLen < len(result):
    grouping = random.randrange(minWords, maxWords+1)
    if groupingLen + grouping > len(result):
      grouping = len(result) - groupingLen
    groupWordsArray.append(grouping)
    groupingLen = groupingLen + grouping
    if groupingLen == prevGroupingLen:
      stuck = stuck + 1
      if stuck > 40:
        print("We are stuck")
        exit()
    prevGroupingLen = groupingLen

  prevValue = 0
  newResult = []
  for value in groupWordsArray:
    value = value + prevValue
    # print("-")
    # print(prevValue)
    # print(value)
    # print("-")
    newResult.append(' '.join(result[prevValue:value]))
    prevValue = value
    if prevValue > 3000 or value > 3000:
      print("Something is wrong")
      exit()

  del result
  del groupWordsArray
  del groupingLen
  del stuck
  del prevGroupingLen
  del prevValue
  numOfWords = len(newResult) + 1
  randomClozeOrder = random.sample(range(1, numOfWords), numOfWords - 1)
  for i, item in enumerate(newResult):
    newResult[i] = "{{c" + str(randomClozeOrder[i]) + "::" + str(item) + "}}"
    
  clozeField = prev + ' ' + ' '.join(newResult)
  my_note = genanki.Note(
    model=genanki.CLOZE_MODEL,
    tags=tag,
    due=due + "1",
    fields=[clozeField, ''])

  cardCount = cardCount + 1
  deck.add_note(my_note)
  # print('Due: ' + due + "1")

  if len(randomClozeOrder) > 1:
    front = 'Finish the ' + length + " that comes next." + "<br>" + prev + '...'
    back = str(prev + ' ' + text)
    another_note = genanki.Note(
      model=genanki.BASIC_MODEL,
      tags=tag,
      due=due + "2",
      fields=[front, back])
    cardCount = cardCount + 1
    deck.add_note(another_note)
    # print('Due: ' + due + "2")


df = pd.read_csv('t_web.csv',
        header=0,
        usecols=["id", "b", "c", "v", "t"])

books = pd.read_csv('key_english.csv')

currentBookNum = 1
currentBook = books.loc[currentBookNum-1, 'field.1']
prevVerse = currentBook + ". "
currentChapter = ''
currentChapterNum = 1
lastLinePrevChap = prevVerse
deck = getBookDeck(currentBook)

print(books.loc[currentBookNum-1, 'field.1'])
print(currentChapterNum, end =" ")
for index, row in df.iterrows():
  primaryText = re.sub(r'\{.*\}', '', row.t)

  due = str(row.id)

  if currentChapterNum != row.c or currentBookNum != row.b:
    createNote(lastLinePrevChap, currentChapter, 'chapter', deck, {str(currentBook).replace(" ", "_") + "::" + "Chapter_"+str(currentChapterNum).zfill(3) + "::Full"}, due)
    print(currentChapterNum, end =" ")
    currentChapterNum = row.c
    lastLinePrevChap = prevVerse # store previous verse for this chapter
    currentChapter = ''
  # elif currentBookNum > 60:
  #   print('Due: ' + due)
    # print('RB: ' + str(row.b))
    # print('CN: ' + str(currentChapterNum))
    # print('RC: ' + str(row.c))
    
  if currentBookNum != row.b:
    # # create chapter card based upon previous chapter
    # createNote(lastLinePrevChap, currentChapter, 'chapter', deck, {str(currentBook).replace(" ", "_") + "::" + "Chapter_"+str(currentChapterNum).zfill(2) + "::Full"}, due)
    # print(currentChapterNum, end =" ")
    # currentChapterNum = row.c
    # currentChapter = ''

    currentBookNum = row.b
    lastLinePrevChap = books.loc[currentBookNum-1, 'field.1'] + ". " # no previous chapter if start of book
    prevVerse = lastLinePrevChap
    genanki.Package(deck).write_to_file("bible/" + currentBook.replace(" ", "_") + '_output.apkg')
    currentBook = books.loc[currentBookNum-1, 'field.1']
    deck = getBookDeck(currentBook)
    print('')
    print(currentBook)

  # # create chapter card based upon previous chapter
  # elif currentChapterNum != row.c:
  #   createNote(lastLinePrevChap, currentChapter, 'chapter', deck, {str(currentBook).replace(" ", "_") + "::" + "Chapter_"+str(currentChapterNum).zfill(3) + "::Full"}, due)
  #   print(currentChapterNum, end =" ")
  #   currentChapterNum = row.c
  #   lastLinePrevChap = prevVerse # store previous verse for this chapter
  #   currentChapter = ''

  # print(primaryText)
  createNote(prevVerse, primaryText, 'verse', deck, {str(currentBook).replace(" ", "_") + "::" + "Chapter_"+str(currentChapterNum).zfill(3) + "::" + "Verse_" + str(row.v).zfill(3)}, due)

  currentChapterNum = row.c
  prevVerse = primaryText
  currentChapter = currentChapter + ' ' + primaryText


createNote(lastLinePrevChap, currentChapter, 'chapter', deck, {str(currentBook).replace(" ", "_") + "::" + "Chapter_"+str(currentChapterNum).zfill(3) + "::Full"}, due)
print(currentChapterNum, end =" ")
print('')
print(cardCount)

genanki.Package(deck).write_to_file("bible/" + currentBook + '.apkg')
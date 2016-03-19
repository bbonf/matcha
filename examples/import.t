  $ python $TESTDIR/../main.py js $TESTDIR/import.tea 2>/dev/null | node
  hello from module
  $ python $TESTDIR/../main.py java $TESTDIR/import.tea 2>/dev/null > Program.java
  $ javac Program.java >/dev/null 2>/dev/null
  $ java Program 2>/dev/null
  hello from module

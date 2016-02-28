  $ python $TESTDIR/../main.py js $TESTDIR/scope.tea 2>/dev/null | node
  5
  8
  5
  $ python $TESTDIR/../main.py java $TESTDIR/scope.tea 2>/dev/null > Program.java
  $ javac Program.java >/dev/null 2>/dev/null
  $ java Program 2>/dev/null
  5
  8
  5

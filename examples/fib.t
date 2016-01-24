  $ python $TESTDIR/../main.py js $TESTDIR/fib.tea 2>/dev/null | node
  1 2 3
  8
  hello world
  $ python $TESTDIR/../main.py java $TESTDIR/fib.tea 2>/dev/null > Program.java
  $ javac Program.java >/dev/null 2>/dev/null
  $ java Program 2>/dev/null
  1 2 3
  8
  hello world

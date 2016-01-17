private static class sys {
    public static void log(Object... msgs) {
        for(Object msg : msgs) {
            System.out.print(msg);
            System.out.print(" ");
        }
        System.out.print("\n");
    }
}

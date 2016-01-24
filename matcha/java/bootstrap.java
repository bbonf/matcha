private static class sys {
    public static void log(Object... msgs) {
        System.out.println(String.join(" ",
            Arrays.asList(msgs)
            .stream().map(x -> { return x.toString(); })
            .collect(Collectors.toList())));
    }
}

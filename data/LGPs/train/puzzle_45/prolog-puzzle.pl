all_members([H], L) :- member(H, L).
all_members([H|T], L) :- member(H, L), all_members(T, L).

all_not_members([H], L) :- not(member(H, L)).
all_not_members([H|T], L) :- not(member(H, L)), all_not_members(T, L).

and([H]) :- H.
and([H|T]) :- H, and(T).

or([H]) :- H, !.
or([H|_]) :- H, !.
or([_|T]) :- or(T).

solve(B0,B1,B2,B3) :-
B0 = [A0, C0],
B1 = [A1, C1],
B2 = [A2, C2],
B3 = [A3, C3],

All = [B0,B1,B2,B3],

all_members([c0, c1, c2, c3], [C0, C1, C2, C3]),
all_members([1, 8, 15, 22], [A0, A1, A2, A3]),
not(A1 = 22),
not(C1 = c0),
not(A1 = 15),
not(member([22, c0], All)),
not(member([15, c0], All)),
and([or([C3 = c1,member([8, c1], All)]), not(and([C3 = c1,member([8, c1], All)]))]),
or([and([C0 = c1,A3 = 22]),and([C3 = c1,A0 = 22])]),
member([C2_val, c2], All),
C2_val-A2=:=14.

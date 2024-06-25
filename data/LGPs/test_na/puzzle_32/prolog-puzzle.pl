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
all_members([1100, 1200, 1300, 1400], [A0, A1, A2, A3]),
member([C0_val, c0], All),
member([C1_val, c1], All),
C0_val<C1_val,
and([or([A2 = 1300,C2 = c1]), not(and([A2 = 1300,C2 = c1]))]),
and([or([member([1400, c2], All),A1 = 1400]), not(and([member([1400, c2], All),A1 = 1400]))]),
C1 = c1,
member([C1_val, c1], All),
A0>C1_val.

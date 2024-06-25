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
all_members([1976, 1979, 1982, 1985], [A0, A1, A2, A3]),
member([C2_val, c2], All),
C2_val-A1=:=6,
and([or([member([1982, c2], All),A1 = 1982]), not(and([member([1982, c2], All),A1 = 1982]))]),
A0 = 1985,
member([1976, c3], All),
and([or([C2 = c0,A2 = 1979]), not(and([C2 = c0,A2 = 1979]))]).

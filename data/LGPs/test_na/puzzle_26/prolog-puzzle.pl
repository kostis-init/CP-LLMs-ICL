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
all_members([480, 540, 600, 660], [A0, A1, A2, A3]),
and([or([A0 = 540,A0 = 480]), not(and([A0 = 540,A0 = 480]))]),
and([or([A1 = 480,C1 = c2]), not(and([A1 = 480,C1 = c2]))]),
A1 = 600,
A2 = 480,
member([C3_val, c3], All),
A1-C3_val=:=120,
not(member([480, c1], All)),
not(member([660, c1], All)).

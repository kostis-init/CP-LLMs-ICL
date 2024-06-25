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
all_members([2001, 2002, 2003, 2004], [A0, A1, A2, A3]),
and([or([member([2004, c3], All),A3 = 2004]), not(and([member([2004, c3], All),A3 = 2004]))]),
or([and([member([2001, c2], All),A2 = 2004]),and([member([2004, c2], All),A2 = 2001])]),
A0>A3,
A1-A0=:=1,
member([C0_val, c0], All),
member([C1_val, c1], All),
C0_val<C1_val.

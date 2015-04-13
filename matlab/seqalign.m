function [ score, alignment ] = seqalign( s, t )
%SEQALIGN

	bins = 10;

	s = [0, s];%(1:30)]
	t = [0, t];%(1:30)];
	
	len_s = length(s);
	len_t = length(t);
	
	if len_s < len_t
		 l = t;
		 t = s;
		 s = l;
	end
	
	len_s = length(s);
	len_t = length(t);

	p = 0;
	q = 4;
	g = 5;

	w = diag(ones(122, 1));
	w(w == 0) = q;
	w(w == 1) = p;

	D = zeros(len_s, len_t);
	P = repmat(char(0), len_s, len_t);
	D(1, 1) = 0;
	P(1, 1) = '*';
	
	D(2:end, 1) = g * ((2:len_s) - 1);
	P(2:end, 1) = '|';

	D(1, 2:end) = g * ((2:len_t) - 1);
	P(1, 2:end) = '-';
	
	for i = 2:len_s
	   for j = 2:len_t
			match = D(i - 1, j - 1) + w(abs(s(i) / 10) + 1, abs(t(j) / 10) + 1);
			delete = D(i - 1, j) + g;	% delete
			insert = D(i, j - 1) + g;	% insert

			D(i, j) = match;
			P(i, j) = '\';
			if delete < D(i, j)
				D(i, j) = delete;
				P(i, j) = '-';
			end
			if insert < D(i, j) 
				D(i, j) = insert;
				P(i, j) = '|';
			end
	   end
	end
	D;
	P;
	
	i = len_s;
	j = len_t;
	g = 1;
	t_al = [];
	% invullen alignment %
	while (i > 0 && j > 0)
		if P(i, j) == '*'
			break
		end
		if P(i, j) == '\'
			s_al(g) = s(i);
			t_al(g) = t(j);
			if s_al(g) == t_al(g)
				l_al(g) = '|';
			else
				l_al(g) = ' ';
			end
			j = j - 1;
					i = i - 1;
		else
			if P(i, j) == '|'
				s_al(g) = s(i);
				t_al(g) = '-';
				l_al(g) = ' ';
				i = i - 1;
			else
				if P(i, j) == '-'
					s_al(g) = '-';
					t_al(g) = t(j);
					l_al(g) = ' ';
					j = j - 1;
				end
			end
		end
		g = g + 1;
	end
	
	score = D(end, end);
end


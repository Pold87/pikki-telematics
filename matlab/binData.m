function [ data ] = binData( input, binsize )
%BINDATA
	data = round(input / binsize) * binsize;
end


#!/usr/bin/perl

use strict;

sub addbackslashes
{
    my $string = shift;
    my $out = "";
    my $char;

    foreach $char (split(//, $string))
    {
        if ($char =~ /[\$\\\"]/)
        {
            $out .= "\\";
        }
        $out .= $char;
    }
    return $out;
}

my $p_expr = & {
    sub {
        my $x = shift;
        return
        "eval {
            my \$local_self;
            \$local_self = sub {
                &{$x}(\"" . addbackslashes($x) . "\");
            };
            &{\$local_self}();
        }";
    }
    }
(
    "sub {
        my \$x = shift;
        return
        \"eval {
            my \\\$local_self;
            \\\$local_self = sub {
                &{\$x}(\\\"\" . addbackslashes(\$x) . \"\\\");
            };
            &{\\\$local_self}();
        }\";
    }"
);

my $p_sub_expr = <<"EOF";
sub {
    my \$x = shift;
    return
    \"eval {
        my \\\$local_self;
        \\\$local_self = sub {
            &{\$x}(\\\"\" . addbackslashes(\$x) . \"\\\");
        };
        &{\\\$local_self}();
    }\";
}
EOF

$p_expr = "&{$p_sub_expr}(\"" . addbackslashes($p_sub_expr) . "\")";

my ($a, $b, @array);

my $evaled = eval($p_expr);
my $evaled_twice = eval($evaled);
if ($evaled eq $evaled_twice)
{
    print "They are the same.\n";
    print "The expression is:\n<<<\n$evaled\n>>>\n";
}
else
{
    print "They are not the same.\n";
}

